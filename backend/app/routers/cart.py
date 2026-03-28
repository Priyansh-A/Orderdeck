from fastapi import Response, status, HTTPException, APIRouter, Depends
from sqlmodel import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone

from ..database import SessionDep
from .. import schemas, auth
from ..models import Cart, CartItem, Product, Table, User
from ..permissions import Permission

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)

@router.get("/", response_model=schemas.CartOut, status_code=status.HTTP_200_OK)
async def get_active_cart(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_CART]))
):
    """Get the current user's active cart"""
    query = (
        select(Cart)
        .where(Cart.user_id == current_user.id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product),
            selectinload(Cart.table)
        )
        .order_by(Cart.created_at.desc())
    )
    
    result = await session.exec(query)
    cart = result.first()
    
    if not cart:
        cart = Cart(user_id=current_user.id)
        session.add(cart)
        await session.commit()
        await session.refresh(cart)
    
    # Build items list
    items_list = []
    subtotal = 0
    total_items = 0
    
    for cart_item in cart.items:
        items_list.append(
            schemas.CartItemOut(
                id=cart_item.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                subtotal=cart_item.subtotal,
                notes=cart_item.notes,
                created_at=cart_item.created_at,
                updated_at=cart_item.updated_at
            )
        )
        subtotal += cart_item.subtotal
        total_items += cart_item.quantity
    
    return schemas.CartOut(
        id=cart.id,
        user_id=cart.user_id,
        table_id=cart.table_id,
        customer_name=cart.customer_name,
        notes=cart.notes,
        created_at=cart.created_at,
        updated_at=cart.updated_at,
        items=items_list,
        subtotal=subtotal,
        total_items=total_items
    )

@router.post("/add-item", response_model=schemas.CartOut, status_code=status.HTTP_200_OK)
async def add_to_cart(
    session: SessionDep,
    item: schemas.CartItemCreate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.ADD_TO_CART]))
):
    # Get or create cart
    cart_query = (
        select(Cart)
        .where(Cart.user_id == current_user.id)
        .order_by(Cart.created_at.desc())
    )
    result = await session.exec(cart_query)
    cart = result.first()
    
    if not cart:
        cart = Cart(user_id=current_user.id)
        session.add(cart)
        await session.flush()
    
    # Get product
    product = await session.get(Product, item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if item already exists
    existing_item = await session.exec(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item.product_id
        )
    )
    existing_item = existing_item.first()
    
    if existing_item:
        existing_item.quantity += item.quantity
        existing_item.subtotal = existing_item.unit_price * existing_item.quantity
        existing_item.notes = item.notes or existing_item.notes
        existing_item.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(existing_item)
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=product.price,
            subtotal=product.price * item.quantity,
            notes=item.notes
        )
        session.add(new_item)
    
    # Update cart timestamp
    cart.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(cart)
    
    await session.commit()
    
    # Don't use the cart object from before, query fresh with joins
    fresh_query = (
        select(Cart)
        .where(Cart.id == cart.id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product),
            selectinload(Cart.table)
        )
    )
    result = await session.exec(fresh_query)
    fresh_cart = result.one()
    
    # Build items list
    items_list = []
    subtotal = 0
    total_items = 0
    
    # Force load items by accessing them (this triggers the eager load)
    cart_items = list(fresh_cart.items)
    
    for cart_item in cart_items:
        items_list.append(
            schemas.CartItemOut(
                id=cart_item.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                subtotal=cart_item.subtotal,
                notes=cart_item.notes,
                created_at=cart_item.created_at,
                updated_at=cart_item.updated_at
            )
        )
        subtotal += cart_item.subtotal
        total_items += cart_item.quantity
    
    return schemas.CartOut(
        id=fresh_cart.id,
        user_id=fresh_cart.user_id,
        table_id=fresh_cart.table_id,
        customer_name=fresh_cart.customer_name,
        notes=fresh_cart.notes,
        created_at=fresh_cart.created_at,
        updated_at=fresh_cart.updated_at,
        items=items_list,
        subtotal=subtotal,
        total_items=total_items
    )

@router.patch("/update-item/{item_id}", response_model=schemas.CartOut, status_code=status.HTTP_200_OK)
async def update_cart_item(
    session: SessionDep,
    item_id: int,
    quantity: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_CART]))
):
    """Update item quantity in cart"""
    cart_item = await session.get(CartItem, item_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    cart = await session.get(Cart, cart_item.cart_id)
    if cart.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your cart")
    
    if quantity <= 0:
        await session.delete(cart_item)
    else:
        cart_item.quantity = quantity
        cart_item.subtotal = cart_item.unit_price * quantity
        cart_item.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(cart_item)
    
    cart.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(cart)
    await session.commit()
    
    query = (
        select(Cart)
        .where(Cart.id == cart.id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product),
            selectinload(Cart.table)
        )
    )
    result = await session.exec(query)
    updated_cart = result.one()
    
    subtotal = sum(item.subtotal for item in updated_cart.items)
    total_items = sum(item.quantity for item in updated_cart.items)
    
    return schemas.CartOut(
        id=updated_cart.id,
        user_id=updated_cart.user_id,
        table_id=updated_cart.table_id,
        customer_name=updated_cart.customer_name,
        notes=updated_cart.notes,
        created_at=updated_cart.created_at,
        updated_at=updated_cart.updated_at,
        items=updated_cart.items,
        subtotal=subtotal,
        total_items=total_items
    )

@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CLEAR_CART]))
):
    """Clear all items from cart and reset table association"""
    cart_query = select(Cart).where(Cart.user_id == current_user.id)
    result = await session.exec(cart_query)
    cart = result.first()
    
    if cart:
        # Delete all cart items
        items_query = select(CartItem).where(CartItem.cart_id == cart.id)
        result = await session.exec(items_query)
        for item in result.all():
            await session.delete(item)
        
        cart.table_id = None
        cart.customer_name = None
        cart.notes = None
        cart.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        
        session.add(cart)
        await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/set-table/{table_id}", response_model=schemas.CartOut, status_code=status.HTTP_200_OK)
async def set_cart_table(
    session: SessionDep,
    table_id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_CART]))
):
    """Set table for dine-in cart"""
    table = await session.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if table.status == "occupied":
        # Check if it's occupied by the same user's party
        if table.occupied_by_party_id:
            # You might want to check if this cart belongs to that party
            pass
        else:
            raise HTTPException(status_code=400, detail="Table is already occupied")
    
    # Get or create cart
    cart_query = select(Cart).where(Cart.user_id == current_user.id).order_by(Cart.created_at.desc())
    result = await session.exec(cart_query)
    cart = result.first()
    
    if not cart:
        cart = Cart(user_id=current_user.id)
        session.add(cart)
        await session.flush()
    
    # Set the table
    cart.table_id = table_id
    cart.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(cart)
    await session.commit()
    
    # Refresh with items
    fresh_query = (
        select(Cart)
        .where(Cart.id == cart.id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product),
            selectinload(Cart.table)
        )
    )
    result = await session.exec(fresh_query)
    fresh_cart = result.one()
    
    subtotal = sum(item.subtotal for item in fresh_cart.items)
    total_items = sum(item.quantity for item in fresh_cart.items)
    
    return schemas.CartOut(
        id=fresh_cart.id,
        user_id=fresh_cart.user_id,
        table_id=fresh_cart.table_id,
        customer_name=fresh_cart.customer_name,
        notes=fresh_cart.notes,
        created_at=fresh_cart.created_at,
        updated_at=fresh_cart.updated_at,
        items=[
            schemas.CartItemOut(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
                notes=item.notes,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            for item in fresh_cart.items
        ],
        subtotal=subtotal,
        total_items=total_items
    )

