from fastapi import Response, status, HTTPException, APIRouter, Depends
from sqlmodel import select, or_
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
# get all tables
@router.get("/", response_model=List[schemas.TableOut], status_code=status.HTTP_200_OK)
async def get_tables(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_TABLES])),
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Get all the tables with filtering and limits
    """
    query = select(Table).where(Table.is_active == True)
    
    if status_filter:
        query = query.where(Table.status == status_filter)
    
    if search:
        query = query.where(Table.table_number.ilike(f"%{search}%"))
    
    query = query.order_by(Table.table_number).offset(skip).limit(limit)
    
    result = await session.exec(query)
    tables = result.all()
    
    return tables

# get only the available tables
@router.get("/available", response_model=List[schemas.TableOut], status_code=status.HTTP_200_OK)
async def get_available_tables(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_TABLES])),
    capacity: Optional[int] = None,
    guest_count: Optional[int] = None
):
    """
    Get all available tables
    """
    query = select(Table).where(
        Table.status == "available",
        Table.is_active == True
    )
    
    # Filter by capacity
    if capacity:
        query = query.where(Table.capacity >= capacity)
    elif guest_count:
        query = query.where(Table.capacity >= guest_count)
    
    query = query.order_by(Table.capacity, Table.table_number)
    
    result = await session.exec(query)
    tables = result.all()
    
    return tables

# get only the occupied and reserved tables
@router.get("/occupied", response_model=List[schemas.TableOut], status_code=status.HTTP_200_OK)
async def get_occupied_tables(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_TABLES]))
):
    """Get all occupied tables"""
    query = select(Table).where(
        Table.status != "available",
        Table.is_active == True        
    ).order_by(Table.table_number)
    
    result = await session.exec(query)
    tables = result.all()
    
    return tables

# get specific table
@router.get("/{id}", response_model=schemas.TableOut, status_code=status.HTTP_200_OK)
async def get_table(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_TABLES]))
):
    """
    Get a specific table by ID with its current orders
    """
    query = select(Table).where(Table.id == id)
    result = await session.exec(query)
    table = result.first()
    
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    return table


#  create table
@router.post("/", response_model=schemas.TableOut, status_code=status.HTTP_201_CREATED)
async def create_table(
    session: SessionDep,
    table: schemas.TableCreate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CREATE_TABLE]))
):
    """
    Create a new table
    """
    # Check if table number already exists
    query = select(Table).where(Table.table_number == table.table_number)
    result = await session.exec(query)
    existing_table = result.first()
    
    if existing_table:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table with number {table.table_number} already exists"
        )
    
    # Create new table
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

# update table
@router.patch("/{id}", response_model=schemas.TableOut, status_code=status.HTTP_200_OK)
async def update_table(
    id: int,
    session: SessionDep,
    table_update: schemas.TableUpdate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_TABLE]))
):
    """
    Update table details
    - **table_number**: New table number (must be unique)
    - **capacity**: New capacity
    - **status**: New status
    """
    # Get existing table
    db_table = await session.get(Table, id)
    
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    # Check if table already exists
    if table_update.table_number and table_update.table_number != db_table.table_number:
        query = select(Table).where(Table.table_number == table_update.table_number)
        result = await session.exec(query)
        existing_table = result.first()
        if existing_table:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table number {table_update.table_number} already exists"
            )
    
    # Update fields
    update_data = table_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_table, field, value)
    
    db_table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(db_table)
    await session.commit()
    await session.refresh(db_table)
    
    return db_table

# update table status
@router.patch("/{id}/status", response_model=schemas.TableOut, status_code=status.HTTP_200_OK)
async def update_table_status(
    id: int,
    session: SessionDep,
    status_update: schemas.TableStatusUpdate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_TABLE_STATUS]))
):
    """
    Update table status (available, occupied)
    """
    db_table = await session.get(Table, id)
    
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    new_status = status_update.status
    
    # Update the status
    db_table.status = new_status
    db_table.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    session.add(db_table)
    await session.commit()
    await session.refresh(db_table)
    
    return db_table

# remove non active tables
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    id: int,
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.DELETE_TABLE]))
):
    """
    Soft delete a table (set is_active=False)
    """
    db_table = await session.get(Table, id)
    
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    # Check if table has active orders
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
    db_table.updated_at = datetime.now(timezone.utc)
    session.add(db_table)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# permanently delete table/force delete
@router.delete("/{id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
async def permanent_delete_table(
    id: int,
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.DELETE_TABLE]))
):
    """
    Permanently delete a table (admin only)
    
    Use with caution! This will remove all order history for this table.
    """
    db_table = await session.get(Table, id)
    
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {id} not found"
        )
    
    # Check if table has any orders
    orders = await session.exec(select(Order).where(Order.table_id == id))
    if orders.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot permanently delete table with order history. Use soft delete instead."
        )
    
    await session.delete(db_table)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# reset all table status to available
@router.post("/reset", status_code=status.HTTP_200_OK)
async def reset_all_tables(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.MANAGE_TABLES]))
):
    """
    Reset all tables to available status
    """
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