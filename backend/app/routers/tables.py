from fastapi import Response, status, HTTPException, APIRouter, Depends
from sqlmodel import select
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
    status_filter: Optional[str] = None
):
    """Get all tables"""
    query = select(Table).where(Table.is_active == True)
    
    if status_filter:
        query = query.where(Table.status == status_filter)
    
    query = query.order_by(Table.table_number).offset(skip).limit(limit)
    
    result = await session.exec(query)
    tables = result.all()
    
    return tables

@router.get("/available", response_model=List[schemas.TableOut], status_code=status.HTTP_200_OK)
async def get_available_tables(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_TABLES])),
    capacity: Optional[int] = None
):
    """Get available tables"""
    query = select(Table).where(
        Table.status == "available",
        Table.is_active == True
    )
    
    if capacity:
        query = query.where(Table.capacity >= capacity)
    
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
        Table.status == "occupied",
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
    """Get a specific table with Id"""
    table = await session.get(Table, id)
    
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
    """Add a table"""
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
        status=table.status.value if hasattr(table, 'status') else "available",
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
    """Update table info"""
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
    """Update table status"""
    db_table = await session.get(Table, id)
    
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    db_table.status = status_update.status.value
    db_table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    if status_update.status == "available":
        db_table.occupied_by_party_id = None
        db_table.occupied_by_customer = None
        db_table.occupied_at = None
    
    session.add(db_table)
    await session.commit()
    await session.refresh(db_table)
    
    return db_table

@router.post("/{id}/occupy", response_model=schemas.TableOut, status_code=status.HTTP_200_OK)
async def occupy_table(
    id: int,
    session: SessionDep,
    customer_name: str,
    party_id: str,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_TABLE_STATUS]))
):
    """Occupy a table"""
    db_table = await session.get(Table, id)
    
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    if db_table.status == "occupied":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table is already occupied by {db_table.occupied_by_customer}"
        )
    
    db_table.status = "occupied"
    db_table.occupied_by_party_id = party_id
    db_table.occupied_by_customer = customer_name
    db_table.occupied_at = datetime.now(timezone.utc).replace(tzinfo=None)
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
    """Delete a table"""
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
            detail="Cannot delete table with active orders"
        )
    
    db_table.is_active = False
    db_table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(db_table)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/reset", status_code=status.HTTP_200_OK)
async def reset_all_tables(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.MANAGE_TABLES]))
):
    """Reset all table status"""
    query = select(Table).where(Table.is_active == True)
    result = await session.exec(query)
    tables = result.all()
    
    reset_count = 0
    for table in tables:
        if table.status != "available":
            table.status = "available"
            table.occupied_by_party_id = None
            table.occupied_by_customer = None
            table.occupied_at = None
            table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            session.add(table)
            reset_count += 1
    
    await session.commit()
    
    return {
        "message": f"Successfully reset {reset_count} tables to available status",
        "total_tables": len(tables),
        "reset_tables": reset_count
    }