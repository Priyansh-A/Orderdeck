from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlmodel import select
from sqlalchemy.orm import selectinload
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import hmac
import hashlib
import base64
import uuid
import json
import os

from ..database import SessionDep
from .. import schemas, auth
from ..models import Payment, Order, Table
from ..permissions import Permission

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

# eSewa Configuration
ESEWA_MERCHANT_CODE = "EPAYTEST"
ESEWA_SECRET_KEY = "8gBm/:&EnhH.1/q"
ESEWA_BASE_URL = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
ESEWA_SUCCESS_URL = "http://localhost:8000/payments/esewa/success"
ESEWA_FAILURE_URL = "http://localhost:8000/payments/esewa/failure"

@router.get("/")
async def get_all_payments(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_PAYMENTS])),
    skip: int = 0,
    limit: int = 100,
    payment_method: Optional[str] = None,
    status_filter: Optional[str] = None
):
    """Get all payments"""
    query = select(Payment)
    
    if payment_method:
        query = query.where(Payment.payment_method == payment_method)
    if status_filter:
        query = query.where(Payment.status == status_filter)
    
    query = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit)
    
    result = await session.exec(query)
    return result.all()

@router.post("/cash/{order_id}")
async def process_cash_payment(
    session: SessionDep,
    order_id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.PROCESS_PAYMENT]))
):
    """Process cash payment"""
    order = await session.get(Order, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")
    
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot process payment for cancelled order")
    
    payment_query = select(Payment).where(Payment.order_id == order_id)
    result = await session.exec(payment_query)
    payment = result.first()
    
    if not payment:
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method="cash",
            status="paid",
            transaction_id=f"CASH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        session.add(payment)
    else:
        payment.status = "paid"
        payment.payment_method = "cash"
        payment.transaction_id = f"CASH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        session.add(payment)
    
    order.payment_status = "paid"
    order.status = "completed"
    order.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(order)
    
    if order.table_id:
        table = await session.get(Table, order.table_id)
        if table and table.status == "occupied":
            table.status = "available"
            table.occupied_by_party_id = None
            table.occupied_by_customer = None
            table.occupied_at = None
            table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            session.add(table)
    
    await session.commit()
    
    return {
        "success": True,
        "payment_id": payment.id,
        "order_id": order.id,
        "order_number": order.order_number,
        "amount": order.total_amount,
        "payment_method": "cash",
        "status": "paid",
        "message": "Payment successful"
    }


@router.post("/esewa/initiate/{order_id}")
async def initiate_esewa_payment(
    session: SessionDep,
    order_id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.PROCESS_PAYMENT]))
):
    """Initiate eSewa payment"""
    
    order = await session.get(Order, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")
    
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot process payment for cancelled order")
    
    existing_payment = await session.exec(
        select(Payment).where(Payment.order_id == order_id)
    )
    existing_payment = existing_payment.first()
    
    if existing_payment and existing_payment.status == "pending":
        await session.delete(existing_payment)
        await session.commit()
    
    total_amount = str(int(order.total_amount))
    transaction_uuid = str(uuid.uuid4())
    
    order.transaction_id = transaction_uuid
    session.add(order)
    await session.commit()
    
    product_code = ESEWA_MERCHANT_CODE
    
    data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    
    secret = bytes(ESEWA_SECRET_KEY, 'utf-8')
    
    hmac_sha256 = hmac.new(secret, data_to_sign.encode('utf-8'), hashlib.sha256)
    signature = base64.b64encode(hmac_sha256.digest()).decode('utf-8')
    
    signed_field_names = "total_amount,transaction_uuid,product_code"
    
    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method="online",
        status="pending",
        transaction_id=transaction_uuid
    )
    session.add(payment)
    await session.commit()
    
    return {
        "success": True,
        "payment_id": payment.id,
        "order_id": order.id,
        "order_number": order.order_number,
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "signature": signature,
        "signed_field_names": signed_field_names,
        "success_url": ESEWA_SUCCESS_URL,
        "failure_url": ESEWA_FAILURE_URL,
        "esewa_url": ESEWA_BASE_URL
    }


@router.get("/esewa/success")
async def esewa_payment_success(
    request: Request,
    session: SessionDep
):
    """eSewa success callback - redirects to frontend"""
    
    encoded_data = request.query_params.get('data', '')
    
    if not encoded_data:
        return RedirectResponse(url="http://localhost:5173/payment/failure?error=no_data")
    
    try:
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        transaction_data = json.loads(decoded_data)
        
        transaction_code = transaction_data.get('transaction_code', '')
        status = transaction_data.get('status', '')
        total_amount = transaction_data.get('total_amount', '')
        transaction_uuid = transaction_data.get('transaction_uuid', '')
        
        order = await session.exec(
            select(Order).where(Order.transaction_id == transaction_uuid)
        )
        order = order.first()
        
        if not order:
            return RedirectResponse(url="http://localhost:5173/payment/failure?error=order_not_found")
        
        if status == 'COMPLETE':
            order.payment_status = "paid"
            order.status = "completed"
            order.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            session.add(order)
            
            payment = await session.exec(
                select(Payment).where(Payment.transaction_id == transaction_uuid)
            )
            payment = payment.first()
            if payment:
                payment.status = "paid"
                payment.transaction_id = transaction_code
                payment.payment_data = json.dumps(transaction_data)
                session.add(payment)
            
            if order.table_id:
                table = await session.get(Table, order.table_id)
                if table and table.status == "occupied":
                    table.status = "available"
                    table.occupied_by_party_id = None
                    table.occupied_by_customer = None
                    table.occupied_at = None
                    table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    session.add(table)
            
            await session.commit()
            
            return RedirectResponse(
                url=f"http://localhost:5173/payment/success?order={order.order_number}&amount={total_amount}&method=esewa"
            )
        else:
            return RedirectResponse(
                url=f"http://localhost:5173/payment/failure?status={status}&order={order.order_number}"
            )
            
    except Exception as e:
        return RedirectResponse(url=f"http://localhost:5173/payment/failure?error={str(e)}")

@router.get("/esewa/failure")
async def esewa_payment_failure(request: Request):
    """eSewa failure callback - redirects to frontend"""
    return RedirectResponse(url="http://localhost:5173/payment/failure?cancelled=true")

@router.get("/verify/{order_id}")
async def verify_payment(
    session: SessionDep,
    order_id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_PAYMENTS]))
):
    """Verify payment status for an order"""
    order = await session.get(Order, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    payment_query = select(Payment).where(Payment.order_id == order_id)
    result = await session.exec(payment_query)
    payment = result.first()
    
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "amount": order.total_amount,
        "payment_status": order.payment_status,
        "order_status": order.status,
        "payment": {
            "id": payment.id if payment else None,
            "method": payment.payment_method if payment else None,
            "status": payment.status if payment else None,
            "transaction_id": payment.transaction_id if payment else None
        } if payment else None
    }