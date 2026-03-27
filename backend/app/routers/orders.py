from fastapi import Response, status, HTTPException, APIRouter, Depends
from sqlmodel import select, and_
from typing import List, Optional
from datetime import datetime, timezone

from ..database import SessionDep
from .. import schemas, auth
from ..models import Order, OrderItem, Product, Table, Payment
from ..permissions import Permission

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# create order
@router.post("/", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    session: SessionDep,
    order: schemas.OrderCreate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CREATE_ORDER]))
):
    """
    Create a new order
    
    - **order_type**: "dine_in" or "takeaway"
    - **table_id**: Required for dine_in orders only
    - **items**: List of products with quantities
    - **customer_name**: Optional for dine_in, recommended for takeaway
    """
    # Generate unique order number (timestamp-based)
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
    
    # Validate based on order type
    if order.order_type == "dine_in":
        if not order.table_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Table ID is required for dine-in orders"
            )
        
        table = await session.get(Table, order.table_id)
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found"
            )
        
        # Table should be occupied or reserved
        if table.status not in ["occupied", "reserved"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table is {table.status}. Table must be occupied or reserved for dine-in orders."
            )
    
    elif order.order_type == "takeaway":
        # For takeaway, table_id should be None
        if order.table_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Table ID should not be provided for takeaway orders"
            )
        
        # Customer name is recommended for takeaway
        if not order.customer_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer name is required for takeaway orders"
            )
    
    # Calculate order totals
    subtotal = 0.0
    order_items = []
    
    for item in order.items:
        product = await session.get(Product, item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found"
            )
        
        if not product.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.name} is not available"
            )
        
        item_subtotal = product.price * item.quantity
        subtotal += item_subtotal
        
        order_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": product.price,
            "subtotal": item_subtotal,
            "notes": item.notes
        })
    
    # Create order
    new_order = Order(
        order_number=order_number,
        order_type=order.order_type,
        table_id=order.table_id if order.order_type == "dine_in" else None,
        user_id=current_user.id,
        customer_name=order.customer_name,
        subtotal=subtotal,
        total_amount=subtotal,
        notes=order.notes
    )
    
    session.add(new_order)
    await session.flush()
    
    # Create order items
    for item_data in order_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            subtotal=item_data["subtotal"],
            notes=item_data.get("notes")
        )
        session.add(order_item)
    
    await session.commit()
    await session.refresh(new_order)
    
    items_result = await session.exec(
        select(OrderItem).where(OrderItem.order_id == new_order.id)
    )
    new_order.items = items_result.all()
    
    return new_order

# get all orders
@router.get("/", response_model=List[schemas.OrderOut], status_code=status.HTTP_200_OK)
async def get_orders(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS])),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    order_type: Optional[str] = None
):
    """Get all orders with optional filters"""
    query = select(Order)
    
    if status:
        query = query.where(Order.status == status)
    if order_type:
        query = query.where(Order.order_type == order_type)
    
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    
    result = await session.exec(query)
    orders = result.all()
    
    # Load items for each order
    for order in orders:
        items_result = await session.exec(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order.items = items_result.all()
    
    return orders

# get active orders
@router.get("/active", response_model=List[schemas.OrderOut], status_code=status.HTTP_200_OK)
async def get_active_orders(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS]))
):
    """Get all orders that are not completed or cancelled"""
    query = select(Order).where(
        Order.status.not_in(["completed", "cancelled"])
    ).order_by(Order.created_at)
    
    result = await session.exec(query)
    orders = result.all()
    
    for order in orders:
        items_result = await session.exec(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order.items = items_result.all()
    
    return orders

# get specific order
@router.get("/{id}", response_model=schemas.OrderOut, status_code=status.HTTP_200_OK)
async def get_order(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS]))
):
    """Get a specific order by ID"""
    order = await session.get(Order, id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found"
        )
    
    # Load order items
    items_result = await session.exec(
        select(OrderItem).where(OrderItem.order_id == order.id)
    )
    order.items = items_result.all()
    
    # Load payment if exists
    payment_result = await session.exec(
        select(Payment).where(Payment.order_id == order.id)
    )
    order.payment = payment_result.first()
    
    return order

# get order by number
@router.get("/number/{order_number}", response_model=schemas.OrderOut, status_code=status.HTTP_200_OK)
async def get_order_by_number(
    session: SessionDep,
    order_number: str,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS]))
):
    """Get order by order number"""
    query = select(Order).where(Order.order_number == order_number)
    result = await session.exec(query)
    order = result.first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with number {order_number} not found"
        )
    
    items_result = await session.exec(
        select(OrderItem).where(OrderItem.order_id == order.id)
    )
    order.items = items_result.all()
    
    return order

# takeaway orders
@router.get("/takeaway", response_model=List[schemas.OrderOut], status_code=status.HTTP_200_OK)
async def get_takeaway_orders(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS])),
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Get all takeaway orders
    """
    query = select(Order).where(Order.order_type == "takeaway")
    
    if status_filter:
        query = query.where(Order.status == status_filter)
    
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    
    result = await session.exec(query)
    orders = result.all()
    
    # Load items for each order
    for order in orders:
        items_result = await session.exec(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order.items = items_result.all()
    
    return orders

@router.patch("/{id}/ready-for-pickup", response_model=schemas.OrderOut, status_code=status.HTTP_200_OK)
async def mark_takeaway_ready(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_ORDER_STATUS]))
):
    """
    Mark a takeaway order as ready for customer pickup
    """
    order = await session.get(Order, id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found"
        )
    
    if order.order_type != "takeaway":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is only for takeaway orders"
        )
    
    if order.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already completed"
        )
    
    # Update order status to ready
    order.status = "ready"
    order.updated_at = datetime.now(timezone.utc)
    
    session.add(order)
    await session.commit()
    await session.refresh(order)
    
    # Load items for response
    items_result = await session.exec(
        select(OrderItem).where(OrderItem.order_id == order.id)
    )
    order.items = items_result.all()
    
    return order


# update order status
@router.patch("/{id}/status", response_model=schemas.OrderOut, status_code=status.HTTP_200_OK)
async def update_order_status(
    session: SessionDep,
    id: int,
    status_update: schemas.OrderStatusUpdate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_ORDER_STATUS]))
):
    """Update order status (pending, preparing, ready, served, completed, cancelled)"""
    order = await session.get(Order, id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found"
        )
    
    old_status = order.status
    new_status = status_update.status
    
    # Validate status transition
    if old_status == "completed" or old_status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update status of {old_status} order"
        )
    
    # Update order status
    order.status = new_status
    order.updated_at = datetime.now(timezone.utc)
    
    # If order is completed or cancelled, free up the table
    if new_status in ["completed", "cancelled"] and order.table_id:
        table = await session.get(Table, order.table_id)
        if table:
            table.status = "available"
            table.updated_at = datetime.now(timezone.utc)
            session.add(table)
    
    session.add(order)
    await session.commit()
    await session.refresh(order)
    
    # Load items for response
    items_result = await session.exec(
        select(OrderItem).where(OrderItem.order_id == order.id)
    )
    order.items = items_result.all()
    
    return order

# cancel order
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CANCEL_ORDER]))
):
    """Cancel an order"""
    order = await session.get(Order, id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found"
        )
    
    if order.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order that is already {order.status}"
        )
    
    # Cancel order
    order.status = "cancelled"
    order.updated_at = datetime.now(timezone.utc)
    
    # Free up table if occupied
    if order.table_id:
        table = await session.get(Table, order.table_id)
        if table and table.status == "occupied":
            table.status = "available"
            table.updated_at = datetime.now(timezone.utc)
            session.add(table)
    
    session.add(order)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)