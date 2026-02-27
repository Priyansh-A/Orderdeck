from .. import schemas, auth
from ..permissions import *
from ..models import Category, Product
from fastapi import Response, status, HTTPException, APIRouter, Depends
from sqlalchemy.orm import selectinload
from sqlmodel import select, func
from ..database import SessionDep
from datetime import datetime
from typing import List, Optional

router = APIRouter(
    prefix="/categories",
    tags=['Categories']
)

@router.get("/", response_model=List[schemas.CategoryOut], status_code=status.HTTP_200_OK)
async def get_categories(
    session: SessionDep,
    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))
    
):
    query = select(Category)
    result = await session.exec(query)
    posts = result.all()

    if not posts:
        return []

    return posts

@router.get("/{id}", response_model=schemas.CategoryOut, status_code=status.HTTP_200_OK)
async def get_category(
    session: SessionDep,
    id: int,
    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))    
):
    post = await session.get(Category, id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Couldn't find a category with id: {id}"
        )
    return post
        
@router.post("/", response_model=schemas.CategoryOut, status_code=status.HTTP_201_CREATED)
async def post_category(
    session: SessionDep, 
    category: schemas.CategoryBase,
    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.CREATE_MENU_ITEM]))
):
    query = select(Category)
    result = query.where(Category.name == category.name)
    post = await session.exec(result)
    existing_category = post.first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    new_category = Category(
        name = category.name
    )
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    
    if not new_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'invalid post input'
        )
    return new_category

@router.patch("/{id}", response_model=schemas.CategoryOut, status_code=status.HTTP_200_OK)
async def update_category(id:int, 
                    session: SessionDep, 
                    category: schemas.CategoryUpdate,
                    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_MENU_ITEM]))
                    ):
    db_post = await session.get(Category,id)
    if db_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"couldn't find a category with id: {id}")
    update_post = category.model_dump(exclude_unset=True)
    for field, value in update_post.items():
        setattr(db_post, field, value)
    db_post.updated_at = datetime.now()
    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)
    return db_post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(id: int, 
                    session: SessionDep,
                    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.DELETE_MENU_ITEM]))
                    ):
    db_post = await session.get(Category,id)
    if db_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"couldn't find a category with id: {id}")
    session.delete(db_post)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)