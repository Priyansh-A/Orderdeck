from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
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
ESEWA_MERCHANT_CODE = os.getenv("ESEWA_MERCHANT_CODE", "EPAYTEST")
ESEWA_SECRET_KEY = os.getenv("ESEWA_SECRET_KEY", "8gBm/:&EnhH.1/q")
ESEWA_BASE_URL = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
ESEWA_SUCCESS_URL = os.getenv("ESEWA_SUCCESS_URL", "http://localhost:5173/payment/success")
ESEWA_FAILURE_URL = os.getenv("ESEWA_FAILURE_URL", "http://localhost:5173/payment/failure")


def generate_esewa_signature(data: Dict[str, Any], secret_key: str) -> str:
    """Generate eSewa signature for payment verification"""
    signed_field_names = data.get("signed_field_names", "")
    field_names = signed_field_names.split(",")
    
    message = ",".join([f"{field}={data.get(field, '')}" for field in field_names])
    
    hmac_sha256 = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    signature = base64.b64encode(hmac_sha256.digest()).decode('utf-8')
    return signature


@router.post("/initiate/{order_id}")
async def initiate_payment(
    session: SessionDep,
    order_id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.PROCESS_PAYMENT]))
):
    """Initiate payment for an order"""
    order = await session.get(Order, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")
    
    if order.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot process payment for cancelled order")
    
    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method="pending",
        status="pending",
        transaction_id=str(uuid.uuid4())
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    
    return {
        "payment_id": payment.id,
        "order_id": order.id,
        "order_number": order.order_number,
        "amount": order.total_amount,
        "status": "pending"
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
    
    total_amount = str(int(order.total_amount))
    transaction_uuid = str(uuid.uuid4())
    
    order.transaction_id = transaction_uuid
    session.add(order)
    await session.commit()
    
    signed_field_names = "total_amount,transaction_uuid,product_code"
    
    payment_data = {
        "amount": "0",
        "tax_amount": "0",
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": ESEWA_MERCHANT_CODE,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": ESEWA_SUCCESS_URL,
        "failure_url": ESEWA_FAILURE_URL,
        "signed_field_names": signed_field_names,
    }
    
    # Generate signature
    signature = generate_esewa_signature(payment_data, ESEWA_SECRET_KEY)
    payment_data["signature"] = signature
    
    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method="online",
        status="pending",
        transaction_id=transaction_uuid,
        payment_data=json.dumps(payment_data)
    )
    session.add(payment)
    await session.commit()
    
    return {
        "payment_id": payment.id,
        "order_id": order.id,
        "order_number": order.order_number,
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "esewa_url": ESEWA_BASE_URL,
        "payment_data": payment_data
    }


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


@router.post("/webhook/esewa")
async def esewa_webhook(request: Request, session: SessionDep):
    """eSewa webhook for payment confirmation"""
    
    try:
        body = await request.json()
        
        transaction_uuid = body.get("transaction_uuid")
        transaction_code = body.get("transaction_code")
        status = body.get("status")
        total_amount = body.get("total_amount")
        
        payment_query = select(Payment).where(Payment.transaction_id == transaction_uuid)
        result = await session.exec(payment_query)
        payment = result.first()
        
        if not payment:
            return JSONResponse(status_code=404, content={"error": "Payment not found"})
        
        if status == "COMPLETE":
            payment.status = "paid"
            payment.transaction_id = transaction_code
            payment.payment_data = json.dumps(body)
            
            order = await session.get(Order, payment.order_id)
            if order:
                order.payment_status = "paid"
                order.status = "completed"
                order.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                
                if order.table_id:
                    table = await session.get(Table, order.table_id)
                    if table and table.status == "occupied":
                        table.status = "available"
                        table.occupied_by_party_id = None
                        table.occupied_by_customer = None
                        table.occupied_at = None
                        table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                        session.add(table)
                
                session.add(order)
            
            session.add(payment)
            await session.commit()
            
            return JSONResponse(content={"success": True})
        else:
            payment.status = "failed"
            payment.payment_data = json.dumps(body)
            session.add(payment)
            await session.commit()
            
            return JSONResponse(content={"success": False, "status": status})
            
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})