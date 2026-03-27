from fastapi import Response, status, HTTPException, APIRouter, Depends
from sqlmodel import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone

from ..database import SessionDep
from .. import schemas, auth
from ..models import Table, Order
from ..permissions import Permission

router = APIRouter(
    prefix="/tables",
    tags=["Tables"]
)


@router.get("/", response_model=List[schemas.TableOut], status_code=status.HTTP_200_OK)
async def get_tables(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_TABLES])),
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    search: Optional[str] = None
):
    """Get All Tables"""
    query = select(Table).where(Table.is_active == True)
    
    if status_filter:
        query = query.where(Table.status == status_filter)
    
    if search:
        query = query.where(Table.table_number.ilike(f"%{search}%"))
    
    query = query.order_by(Table.table_number).offset(skip).limit(limit)
    
    result = await session.exec(query)
    tables = result.all()
    
    return tables

@router.get("/available", response_model=List[schemas.TableOut], status_code=status.HTTP_200_OK)
async def get_available_tables(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_TABLES])),
    capacity: Optional[int] = None,
    guest_count: Optional[int] = None
):
    """Only get Available tables"""
    query = select(Table).where(
        Table.status == "available",
        Table.is_active == True
    )
    
    if capacity:
        query = query.where(Table.capacity >= capacity)
    elif guest_count:
        query = query.where(Table.capacity >= guest_count)
    
    query = query.order_by(Table.capacity, Table.table_number)
    
    result = await session.exec(query)
    tables = result.all()
    
    return tables

@router.get("/occupied", response_model=List[schemas.TableOut], status_code=status.HTTP_200_OK)
async def get_occupied_tables(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_TABLES]))
):
    """Get occupied tables"""
    query = select(Table).where(
        Table.status != "available",
        Table.is_active == True        
    ).order_by(Table.table_number)
    
    result = await session.exec(query)
    tables = result.all()
    
    return tables

@router.get("/{id}", response_model=schemas.TableOut, status_code=status.HTTP_200_OK)
async def get_table(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_TABLES]))
):
    """Get tables through Id"""
    query = select(Table).where(Table.id == id)
    result = await session.exec(query)
    table = result.first()
    
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    return table

@router.post("/", response_model=schemas.TableOut, status_code=status.HTTP_201_CREATED)
async def create_table(
    session: SessionDep,
    table: schemas.TableCreate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CREATE_TABLE]))
):
    """Add a Table"""
    query = select(Table).where(Table.table_number == table.table_number)
    result = await session.exec(query)
    existing_table = result.first()
    
    if existing_table:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table with number {table.table_number} already exists"
        )
    
    new_table = Table(
        table_number=table.table_number,
        capacity=table.capacity,
        status=table.status if hasattr(table, 'status') else "available",
        is_active=True
    )
    
    session.add(new_table)
    await session.commit()
    await session.refresh(new_table)
    
    return new_table

@router.patch("/{id}", response_model=schemas.TableOut, status_code=status.HTTP_200_OK)
async def update_table(
    id: int,
    session: SessionDep,
    table_update: schemas.TableUpdate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_TABLE]))
):
    """Update table data"""
    db_table = await session.get(Table, id)
    
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    if table_update.table_number and table_update.table_number != db_table.table_number:
        query = select(Table).where(Table.table_number == table_update.table_number)
        result = await session.exec(query)
        existing_table = result.first()
        if existing_table:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table number {table_update.table_number} already exists"
            )
    
    update_data = table_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_table, field, value)
    
    db_table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(db_table)
    await session.commit()
    await session.refresh(db_table)
    
    return db_table

@router.patch("/{id}/status", response_model=schemas.TableOut, status_code=status.HTTP_200_OK)
async def update_table_status(
    id: int,
    session: SessionDep,
    status_update: schemas.TableStatusUpdate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_TABLE_STATUS]))
):
    """Update Table Status"""
    db_table = await session.get(Table, id)
    
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    db_table.status = status_update.status
    db_table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    session.add(db_table)
    await session.commit()
    await session.refresh(db_table)
    
    return db_table

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    id: int,
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.DELETE_TABLE]))
):
    """Soft delete tables that are empty"""
    db_table = await session.get(Table, id)
    
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    active_orders = await session.exec(
        select(Order).where(
            Order.table_id == id,
            Order.status.not_in(["completed", "cancelled"])
        )
    )
    
    if active_orders.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete table with active orders. Complete or cancel orders first."
        )
    
    db_table.is_active = False
    db_table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(db_table)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/{id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
async def permanent_delete_table(
    id: int,
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.DELETE_TABLE]))
):
    """Force Delete Tables"""
    db_table = await session.get(Table, id)
    
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    orders = await session.exec(select(Order).where(Order.table_id == id))
    if orders.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot permanently delete table with order history. Use soft delete instead."
        )
    
    await session.delete(db_table)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/reset", status_code=status.HTTP_200_OK)
async def reset_all_tables(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.MANAGE_TABLES]))
):
    """Reset all table status to available"""
    query = select(Table).where(Table.is_active == True)
    result = await session.exec(query)
    tables = result.all()
    
    reset_count = 0
    for table in tables:
        if table.status != "available":
            table.status = "available"
            table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            session.add(table)
            reset_count += 1
    
    await session.commit()
    
    return {
        "message": f"Successfully reset {reset_count} tables to available status",
        "total_tables": len(tables),
        "reset_tables": reset_count
    }

@router.post("/{id}/close-session", status_code=status.HTTP_200_OK)
async def close_table_session(
    id: int,
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.MANAGE_TABLES]))
):
    """Close Table Session """
    from ..services.table_session import TableSessionManager
    
    result = await TableSessionManager.close_table_session(session, id, current_user)
    return result

@router.get("/{id}/session-info", status_code=status.HTTP_200_OK)
async def get_table_session_info(
    id: int,
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_TABLES]))
):
    """Details on the table session"""
    from ..services.table_session import TableSessionManager
    
    result = await TableSessionManager.get_table_session_info(session, id)
    return result