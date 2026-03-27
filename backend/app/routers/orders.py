from fastapi import Response, status, HTTPException, APIRouter, Depends
from sqlmodel import select, and_
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import selectinload
from ..database import SessionDep
from .. import schemas, auth
from ..models import Order, OrderItem, Product, Table, Payment
from ..permissions import Permission
from ..services.table_session import TableSessionManager

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)
# add orders
@router.post("/", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    session: SessionDep,
    order: schemas.OrderCreate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CREATE_ORDER]))
):
    """ Creating orders """
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{current_user.id}"
    
    table = None
    party_id = None
    
    if order.order_type == "dine_in":
        if not order.table_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Table ID is required for dine-in orders"
            )
        
        if not order.customer_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer name is required for dine-in orders"
            )
        
        table, party_id = await TableSessionManager.validate_and_get_party(
            session, 
            order.table_id, 
            order.customer_name,
            order.order_type
        )
    
    product_counts = {}
    for item in order.items:
        if item.product_id in product_counts:
            product_counts[item.product_id] += item.quantity
        else:
            product_counts[item.product_id] = item.quantity
    
    subtotal = 0.0
    order_items_data = []
    
    for product_id, quantity in product_counts.items():
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        
        item_subtotal = product.price * quantity
        subtotal += item_subtotal
        
        order_items_data.append({
            "product_id": product.id,
            "quantity": quantity,
            "unit_price": product.price,
            "subtotal": item_subtotal,
            "notes": None
        })
    
    new_order = Order(
        order_number=order_number,
        order_type=order.order_type,
        table_id=order.table_id if order.order_type == "dine_in" else None,
        party_id=party_id,
        user_id=current_user.id,
        customer_name=order.customer_name,
        subtotal=subtotal,
        total_amount=subtotal,
        notes=order.notes
    )
    
    session.add(new_order)
    await session.flush()
    
    if order.order_type == "dine_in" and table and table.status == "available":
        table.status = "occupied"
        table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(table)
    
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            subtotal=item_data["subtotal"],
            notes=item_data.get("notes")
        )
        session.add(order_item)
    
    await session.commit()
    
    query = (
        select(Order)
        .where(Order.id == new_order.id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.table),
            selectinload(Order.user),
            selectinload(Order.payment)
        )
    )
    
    result = await session.exec(query)
    refreshed_order = result.one()
    
    return refreshed_order

# add more items to the order
@router.post("/{order_id}/add-items", response_model=schemas.OrderOut)
async def add_items_to_order(
    session: SessionDep,
    order_id: int,
    items: List[schemas.OrderItemCreate],
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CREATE_ORDER]))
):
    """Add more items to an order"""
    order = await session.get(Order, order_id)
    
    if not order:
        raise HTTPException(404, "Order not found")
    
    if order.status in ["completed", "cancelled"]:
        raise HTTPException(400, f"Cannot add items to {order.status} order")
    
    if order.order_type == "dine_in" and order.table_id:
        table = await session.get(Table, order.table_id)
        if table.status != "occupied":
            raise HTTPException(400, "Table is no longer occupied")
    
    product_counts = {}
    for item in items:
        if item.product_id in product_counts:
            product_counts[item.product_id] += item.quantity
        else:
            product_counts[item.product_id] = item.quantity
    
    for product_id, quantity in product_counts.items():
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(404, f"Product {product_id} not found")
        
        existing_item = None
        for existing in order.items:
            if existing.product_id == product_id:
                existing_item = existing
                break
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.subtotal = existing_item.unit_price * existing_item.quantity
            session.add(existing_item)
        else:
            new_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price,
                subtotal=product.price * quantity,
                notes=None
            )
            session.add(new_item)
        
        order.subtotal += product.price * quantity
        order.total_amount = order.subtotal
    
    order.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(order)
    await session.commit()
    
    query = select(Order).where(Order.id == order.id).options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.table),
        selectinload(Order.user),
        selectinload(Order.payment)
    )
    result = await session.exec(query)
    return result.one()

@router.get("/", response_model=List[schemas.OrderOut], status_code=status.HTTP_200_OK)
async def get_orders(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS])),
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    order_type: Optional[str] = None
):
    """Get all orders"""
    query = select(Order)
    
    if status_filter:
        query = query.where(Order.status == status_filter)
    if order_type:
        query = query.where(Order.order_type == order_type)
    
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    query = query.options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.table),
        selectinload(Order.user),
        selectinload(Order.payment)
    )
    
    result = await session.exec(query)
    orders = result.all()
    
    return orders

@router.get("/active", response_model=List[schemas.OrderOut], status_code=status.HTTP_200_OK)
async def get_active_orders(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS]))
):
    """Only get active orders"""
    query = select(Order).where(
        Order.status.not_in(["completed", "cancelled"])
    ).order_by(Order.created_at)
    
    query = query.options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.table),
        selectinload(Order.user),
        selectinload(Order.payment)
    )
    
    result = await session.exec(query)
    orders = result.all()
    
    return orders

@router.get("/{id}", response_model=schemas.OrderOut, status_code=status.HTTP_200_OK)
async def get_order(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS]))
):
    """Orders with specific id"""
    query = select(Order).where(Order.id == id).options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.table),
        selectinload(Order.user),
        selectinload(Order.payment)
    )
    
    result = await session.exec(query)
    order = result.first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found"
        )
    
    return order

@router.get("/number/{order_number}", response_model=schemas.OrderOut, status_code=status.HTTP_200_OK)
async def get_order_by_number(
    session: SessionDep,
    order_number: str,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS]))
):
    """Orders with specific order number"""
    query = select(Order).where(Order.order_number == order_number).options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.table),
        selectinload(Order.user),
        selectinload(Order.payment)
    )
    
    result = await session.exec(query)
    order = result.first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with number {order_number} not found"
        )
    
    return order

@router.get("/takeaway", response_model=List[schemas.OrderOut], status_code=status.HTTP_200_OK)
async def get_takeaway_orders(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS])),
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get only the takeaway orders"""
    query = select(Order).where(Order.order_type == "takeaway")
    
    if status_filter:
        query = query.where(Order.status == status_filter)
    
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    query = query.options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.user),
        selectinload(Order.payment)
    )
    
    result = await session.exec(query)
    orders = result.all()
    
    return orders

@router.patch("/{id}/ready-for-pickup", response_model=schemas.OrderOut, status_code=status.HTTP_200_OK)
async def mark_takeaway_ready(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_ORDER_STATUS]))
):
    """Change status of takeaway products"""
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
    
    order.status = "ready"
    order.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    session.add(order)
    await session.commit()
    
    query = select(Order).where(Order.id == id).options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.table),
        selectinload(Order.user),
        selectinload(Order.payment)
    )
    
    result = await session.exec(query)
    refreshed_order = result.one()
    
    return refreshed_order

@router.patch("/{id}/status", response_model=schemas.OrderOut, status_code=status.HTTP_200_OK)
async def update_order_status(
    session: SessionDep,
    id: int,
    status_update: schemas.OrderStatusUpdate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_ORDER_STATUS]))
):
    """Change status of orders"""
    order = await session.get(Order, id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found"
        )
    
    if order.status == "completed" or order.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update status of {order.status} order"
        )
    
    order.status = status_update.status
    order.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    session.add(order)
    await session.commit()
    
    query = select(Order).where(Order.id == id).options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.table),
        selectinload(Order.user),
        selectinload(Order.payment)
    )
    
    result = await session.exec(query)
    refreshed_order = result.one()
    
    return refreshed_order

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
    
    order.status = "cancelled"
    order.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    if order.table_id:
        other_active = await session.exec(
            select(Order).where(
                Order.table_id == order.table_id,
                Order.status.not_in(["completed", "cancelled"]),
                Order.id != order.id
            )
        )
        
        if not other_active.first():
            table = await session.get(Table, order.table_id)
            if table and table.status == "occupied":
                table.status = "available"
                table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                session.add(table)
    
    session.add(order)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)