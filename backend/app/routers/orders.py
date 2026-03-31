from fastapi import Response, status, HTTPException, APIRouter, Depends
from sqlmodel import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone

from ..database import SessionDep
from .. import schemas, auth
from ..models import Order, OrderItem, Product, Table, Payment, User, Cart, CartItem
from ..permissions import Permission

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post("/checkout", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
async def checkout(
    session: SessionDep,
    checkout_data: schemas.CheckoutRequest,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CHECKOUT]))
):
    """Convert cart to order"""
    
    # Load eagerly
    cart_query = (
        select(Cart)
        .where(Cart.id == checkout_data.cart_id, Cart.user_id == current_user.id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product),
            selectinload(Cart.table)
        )
    )
    result = await session.exec(cart_query)
    cart = result.first()
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    table = None
    party_id = None
    
    if checkout_data.order_type == "dine_in":
        if not cart.table_id:
            raise HTTPException(status_code=400, detail="Table ID required for dine-in")
        
        table = await session.get(Table, cart.table_id)
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        
        if table.status == "occupied":
            raise HTTPException(
                status_code=400, 
                detail=f"Table {table.table_number} is already occupied by {table.occupied_by_customer or 'another party'}"
            )
        
        party_id = f"PARTY-{table.id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        table.status = "occupied"
        table.occupied_by_party_id = party_id
        table.occupied_by_customer = checkout_data.customer_name or cart.customer_name
        table.occupied_at = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(table)
    
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{current_user.id}"
    
    subtotal = 0
    order_items_data = []
    
    for cart_item in cart.items:
        product = cart_item.product
        if not product:
            product = await session.get(Product, cart_item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {cart_item.product_id} not found")
        
        item_subtotal = product.price * cart_item.quantity
        subtotal += item_subtotal
        
        order_items_data.append({
            "product_id": product.id,
            "quantity": cart_item.quantity,
            "unit_price": product.price,
            "subtotal": item_subtotal,
            "notes": cart_item.notes
        })
    
    total = subtotal 
    
    new_order = Order(
        order_number=order_number,
        order_type=checkout_data.order_type,
        table_id=cart.table_id if checkout_data.order_type == "dine_in" else None,
        party_id=party_id,
        user_id=current_user.id,
        customer_name=checkout_data.customer_name or cart.customer_name,
        customer_phone=checkout_data.customer_phone,
        subtotal=subtotal,
        total_amount=total,
        notes=checkout_data.notes or cart.notes
    )
    
    session.add(new_order)
    await session.flush()
    
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
    
    for cart_item in cart.items:
        await session.delete(cart_item)
    
    await session.delete(cart)
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
    """Get all Orders"""
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
    return result.all()

@router.get("/active", response_model=List[schemas.OrderOut], status_code=status.HTTP_200_OK)
async def get_active_orders(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS]))
):
    """Get active orders"""
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
    return result.all()

@router.get("/{id}", response_model=schemas.OrderOut, status_code=status.HTTP_200_OK)
async def get_order(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_ORDERS]))
):
    """Get specific order with Id"""
    query = select(Order).where(Order.id == id).options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.table),
        selectinload(Order.user),
        selectinload(Order.payment)
    )
    
    result = await session.exec(query)
    order = result.first()
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
    
    return order

@router.patch("/{id}/status", response_model=schemas.OrderOut, status_code=status.HTTP_200_OK)
async def update_order_status(
    session: SessionDep,
    id: int,
    status_update: schemas.OrderStatusUpdate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_ORDER_STATUS]))
):
    """Update Order Status"""
    order = await session.get(Order, id)
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
    
    if order.status in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot update status of {order.status} order")
    
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
    return result.one()

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
    
    if order.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot mark cancelled order as ready"
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


@router.delete("/{id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
async def permanent_delete_order(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.DELETE_ORDER]))
):
    """
    Permanently delete an order
    """
    order = await session.get(Order, id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {id} not found"
        )
    
    payment = await session.exec(
        select(Payment).where(Payment.order_id == id)
    )
    payment = payment.first()
    
    if payment:
        await session.delete(payment)
    
    items = await session.exec(
        select(OrderItem).where(OrderItem.order_id == id)
    )
    for item in items.all():
        await session.delete(item)
    
    await session.delete(order)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CANCEL_ORDER]))
):
    """Cancel an order"""
    order = await session.get(Order, id)
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
    
    if order.status in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel order that is already {order.status}")
    
    order.status = "cancelled"
    order.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    session.add(order)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)