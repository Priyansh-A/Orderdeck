from .. import schemas, utils, auth
from ..models import User
from fastapi import status, HTTPException, APIRouter, Depends, Response
from sqlmodel import select
from ..database import SessionDep
from ..permissions import *
from datetime import datetime, timezone
from typing import List

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(
    user: schemas.UserCreate,
    session: SessionDep
):
    """Add a user"""
    query = select(User).where(
        (User.username == user.username) | 
        (User.email == user.email)
    )
    result = await session.exec(query)
    existing = result.first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    hashed_password = utils.password_hash.hash(user.password)
    user.password = hashed_password
    
    new_user = User(**user.model_dump())
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

@router.get("/", response_model=List[schemas.UserOut], status_code=status.HTTP_200_OK)
async def get_users(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_STAFF]))
):
    """Get all users"""
    query = select(User)
    result = await session.exec(query)
    users = result.all()
    
    return users

@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(
    id: int,
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_STAFF]))
):
    """Get specific user with Id"""
    user = await session.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist")
    return user

@router.patch("/{id}", response_model=schemas.UserOut)
async def update_user(
    id: int, 
    user_update: schemas.UserUpdate,
    session: SessionDep, 
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.MANAGE_STAFF]))
):
    """Update user info"""
    db_user = await session.get(User, id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Couldn't find a user with id: {id}")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.created_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: int,
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.MANAGE_STAFF]))
):
    """Remove a user"""
    deleted_user = await session.get(User, id)
    if deleted_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist")
    
    await session.delete(deleted_user)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)