from .. import schemas, auth
from ..permissions import *
from ..models import Category
from fastapi import Response, status, HTTPException, APIRouter, Depends
from sqlalchemy.orm import selectinload
from sqlmodel import select
from ..database import SessionDep
from datetime import datetime, timezone
from typing import List

router = APIRouter(
    prefix="/categories",
    tags=['Categories']
)

@router.get("/", response_model=List[schemas.CategoryOut], status_code=status.HTTP_200_OK)
async def get_categories(
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))
):
    query = select(Category)
    result = await session.exec(query)
    categories = result.all()
    
    if not categories:
        return []
    
    return categories

@router.get("/{id}", response_model=schemas.CategoryOut, status_code=status.HTTP_200_OK)
async def get_category(
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))    
):
    category = await session.get(Category, id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Couldn't find a category with id: {id}"
        )
    return category
        
@router.post("/", response_model=schemas.CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    session: SessionDep, 
    category: schemas.CategoryCreate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CREATE_MENU_ITEM]))
):
    query = select(Category).where(Category.name == category.name)
    result = await session.exec(query)
    existing_category = result.first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    new_category = Category(name=category.name)
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    
    return new_category

@router.patch("/{id}", response_model=schemas.CategoryOut, status_code=status.HTTP_200_OK)
async def update_category(
    id: int, 
    session: SessionDep, 
    category: schemas.CategoryUpdate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_MENU_ITEM]))
):
    db_category = await session.get(Category, id)
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Couldn't find a category with id: {id}")
    
    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db_category.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    id: int, 
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.DELETE_MENU_ITEM]))
):
    db_category = await session.get(Category, id)
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Couldn't find a category with id: {id}")
    
    await session.delete(db_category)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)