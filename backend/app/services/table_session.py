# services/table_session.py
from datetime import datetime, timezone
from typing import Tuple, Optional
from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.orm import selectinload

from ..database import SessionDep
from ..models import Table, Order, OrderItem, Payment


class TableSessionManager:
    """Manages table sessions to ensure one party per table"""
    
    @staticmethod
    async def generate_party_id(table_id: int) -> str:
        """Generate a unique party ID for a table session"""
        return f"PARTY-{table_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    @staticmethod
    async def validate_and_get_party(
        session: SessionDep,
        table_id: int,
        customer_name: str,
        order_type: str
    ) -> Tuple[Table, Optional[str]]:
        """
        Validate that a customer can place an order at a table.
        Returns (table, party_id) if valid, raises HTTPException otherwise.
        """
        if order_type != "dine_in":
            return None, None
        
        table = await session.get(Table, table_id)
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table with id {table_id} not found"
            )
        
        if not table.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table {table.table_number} is not active"
            )
        
        if table.status == "available":
            party_id = await TableSessionManager.generate_party_id(table_id)
            return table, party_id
        
        if table.status == "occupied":
            query = (
                select(Order)
                .where(
                    Order.table_id == table_id,
                    Order.status.not_in(["completed", "cancelled"])
                )
                .order_by(Order.created_at)
            )
            result = await session.exec(query)
            active_order = result.first()
            
            if not active_order:
                table.status = "available"
                session.add(table)
                await session.flush()
                party_id = await TableSessionManager.generate_party_id(table_id)
                return table, party_id
            
            if active_order.customer_name != customer_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Table {table.table_number} is currently occupied by {active_order.customer_name}. "
                        f"Please wait until they leave or use a different table."
                )
            
            return table, active_order.party_id
        
        if table.status == "reserved":
            query = (
                select(Order)
                .where(
                    Order.table_id == table_id,
                    Order.status.not_in(["completed", "cancelled"])
                )
            )
            result = await session.exec(query)
            active_order = result.first()
            
            if active_order:
                if active_order.customer_name != customer_name:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Table {table.table_number} is reserved for {active_order.customer_name}"
                    )
                return table, active_order.party_id
            
            party_id = await TableSessionManager.generate_party_id(table_id)
            return table, party_id
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table {table.table_number} is {table.status}. Cannot place orders."
        )
    
    @staticmethod
    async def close_table_session(
        session: SessionDep,
        table_id: int,
        current_user
    ) -> dict:
        """
        Close the table session (customers have left)
        Should be called after final payment
        """
        table = await session.get(Table, table_id)
        
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table with id {table_id} not found"
            )
        
        unpaid_query = (
            select(Order)
            .where(
                Order.table_id == table_id,
                Order.payment_status != "paid",
                Order.status.not_in(["completed", "cancelled"])
            )
        )
        
        result = await session.exec(unpaid_query)
        unpaid_orders = result.all()
        
        if unpaid_orders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot close table session. There are unpaid orders. Please process payment first."
            )
        
        all_orders_query = (
            select(Order)
            .where(
                Order.table_id == table_id,
                Order.status.not_in(["cancelled"])
            )
            .order_by(Order.created_at)
        )
        
        result = await session.exec(all_orders_query)
        orders_list = result.all()
        
        order_numbers = [order.order_number for order in orders_list]
        
        old_status = table.status
        table.status = "available"
        table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(table)
        await session.commit()
        
        return {
            "message": f"Table {table.table_number} is now available",
            "table_id": table.id,
            "table_number": table.table_number,
            "previous_status": old_status,
            "orders_closed": len(orders_list),
            "total_orders": order_numbers
        }
    
    @staticmethod
    async def get_table_session_info(
        session: SessionDep,
        table_id: int
    ) -> dict:
        """
        Get information about the current table session
        """
        table = await session.get(Table, table_id)
        
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table with id {table_id} not found"
            )
        
        active_orders_query = (
            select(Order)
            .where(
                Order.table_id == table_id,
                Order.status.not_in(["completed", "cancelled"])
            )
            .order_by(Order.created_at)
        )
        
        result = await session.exec(active_orders_query)
        active_orders_list = result.all()
        
        completed_orders_query = (
            select(Order)
            .where(
                Order.table_id == table_id,
                Order.status == "completed"
            )
            .order_by(Order.created_at)
        )
        
        result = await session.exec(completed_orders_query)
        completed_orders_list = result.all()
        
        total_unpaid = 0
        for order in active_orders_list:
            if order.payment_status != "paid":
                total_unpaid += order.total_amount
        
        party_info = None
        if active_orders_list:
            first_order = active_orders_list[0]
            party_info = {
                "customer_name": first_order.customer_name,
                "party_id": first_order.party_id,
                "order_count": len(active_orders_list),
                "total_amount": sum(o.total_amount for o in active_orders_list)
            }
        
        return {
            "table": {
                "id": table.id,
                "number": table.table_number,
                "status": table.status,
                "capacity": table.capacity
            },
            "session_active": table.status in ["occupied", "reserved"],
            "active_orders": len(active_orders_list),
            "completed_orders": len(completed_orders_list),
            "total_unpaid_amount": total_unpaid,
            "party_info": party_info
        }
    
    @staticmethod
    async def get_table_orders(
        session: SessionDep,
        table_id: int,
        include_completed: bool = False
    ) -> list:
        """
        Get all orders for a specific table
        """
        query = select(Order).where(Order.table_id == table_id)
        
        if not include_completed:
            query = query.where(Order.status.not_in(["completed", "cancelled"]))
        
        query = query.order_by(Order.created_at)
        
        result = await session.exec(query)
        return result.all()
    
    @staticmethod
    async def get_table_session_info_with_items(
        session: SessionDep,
        table_id: int
    ) -> dict:
        """Get table session info with order items (if needed)"""
        table = await session.get(Table, table_id)
        
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        
        # Eager load items BEFORE any operations
        query = (
            select(Order)
            .where(
                Order.table_id == table_id,
                Order.status.not_in(["completed", "cancelled"])
            )
            .order_by(Order.created_at)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product)
            )
        )
        
        result = await session.exec(query)
        active_orders = result.all()
        
        # Now you can safely access order.items
        items_list = []
        for order in active_orders:
            for item in order.items:
                items_list.append({
                    "order_id": order.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": item.unit_price
                })
        
        return {
            "table": table.table_number,
            "items": items_list
        }