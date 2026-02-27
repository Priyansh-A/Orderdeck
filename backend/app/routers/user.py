from .. import schemas, utils, auth
from ..models import User
from fastapi import status, HTTPException,  APIRouter, Depends, Response
from sqlmodel import select
from ..database import SessionDep
from ..permissions import *
from datetime import datetime
from typing import List

router = APIRouter(
    prefix="/users",
    tags = ['Users']
)

# create user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate , session : SessionDep):
    
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
        
    # hash password
    hashed_password = utils.password_hash.hash(user.password)
    user.password = hashed_password
    
    new_user = User(**user.model_dump())
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

# get all users
@router.get("/", response_model=List[schemas.UserOut], status_code=status.HTTP_200_OK)
async def get_users(
    session: SessionDep,
    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_STAFF]))
    
):
    query = select(User)
    result = await session.exec(query)
    users = result.all()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Couldn't find any categories"
        )

    return users

#  get a specific user
@router.get("/{id}",response_model=schemas.UserOut)
async def get_user(
                    id: int,
                    session: SessionDep,
                    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_STAFF]))):
    query = select(User).where(User.id == id)
    result = await session.exec(query)
    user = result.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist")
    return user

# edit user credentials
@router.put("/{id}", response_model=schemas.UserUpdate)
async def update_user(
                id: int, 
                user_update: schemas.UserUpdate,
                session: SessionDep, 
                current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.MANAGE_STAFF]))):
    db_user = await session.get(User, id)
    if db_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"couldn't find a user with id: {id}")
    update_user = user_update.model_dump(exclude_unset=True)
    for field, value in update_user.items():
        setattr(db_user, field, value)
    db_user.created_at = datetime.now()
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


# delete a specific user
@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_posts(
    id: int,
    session: SessionDep,
    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.MANAGE_STAFF]))):
    deleted_user = await session.get(User, id)
    if deleted_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"user with id: {id} does not exist")
    await session.delete(deleted_user)
    await session.commit()
    return  Response(status_code = status.HTTP_204_NO_CONTENT)