from fastapi import Response, status, HTTPException, APIRouter, Depends
from sqlmodel import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone

from ..database import SessionDep
from .. import schemas, auth
from ..models import Payment, Order, Table
from ..permissions import Permission

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

@router.post("/", response_model=schemas.PaymentOut, status_code=status.HTTP_201_CREATED)
async def process_payment(
    session: SessionDep,
    payment: schemas.PaymentCreate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.PROCESS_PAYMENT]))
):
    order = await session.get(Order, payment.order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {payment.order_id} not found"
        )
    
    if order.payment_status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is already paid"
        )
    
    if order.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot process payment for cancelled order"
        )
    
    if payment.payment_method == "online" and not payment.transaction_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction ID is required for online payments"
        )
    
    new_payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method=payment.payment_method,
        transaction_id=payment.transaction_id,
        payment_data=payment.payment_data
    )
    
    order.payment_status = "paid"
    order.status = "completed"
    order.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    session.add(new_payment)
    session.add(order)
    await session.commit()
    await session.refresh(new_payment)
    
    return new_payment

@router.get("/order/{order_id}", response_model=schemas.PaymentOut, status_code=status.HTTP_200_OK)
async def get_payment_by_order(
    session: SessionDep,
    order_id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_PAYMENTS]))
):
    query = select(Payment).where(Payment.order_id == order_id)
    result = await session.exec(query)
    payment = result.first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment for order {order_id} not found"
        )
    
    return payment

@router.get("/", response_model=List[schemas.PaymentOut], status_code=status.HTTP_200_OK)
async def get_all_payments(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_PAYMENTS])),
    skip: int = 0,
    limit: int = 100,
    payment_method: Optional[str] = None,
    status_filter: Optional[str] = None
):
    query = select(Payment)
    
    if payment_method:
        query = query.where(Payment.payment_method == payment_method)
    if status_filter:
        query = query.where(Payment.status == status_filter)
    
    query = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit)
    
    result = await session.exec(query)
    return result.all()

@router.post("/{id}/refund", response_model=schemas.PaymentOut, status_code=status.HTTP_200_OK)
async def refund_payment(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.REFUND_PAYMENT]))
):
    payment = await session.get(Payment, id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with id {id} not found"
        )
    
    if payment.status != "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only paid payments can be refunded"
        )
    
    payment.status = "refunded"
    session.add(payment)
    
    order = await session.get(Order, payment.order_id)
    if order:
        order.payment_status = "failed"
        order.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(order)
    
    await session.commit()
    await session.refresh(payment)
    
    return payment