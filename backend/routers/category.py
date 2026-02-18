from .. import schemas
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
def get_categories(
    session: SessionDep,
):
    query = select(Category)
    result = session.exec(query)
    posts = result.all()

    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Couldn't find any categories"
        )

    return posts

@router.get("/{id}", response_model=schemas.CategoryOut, status_code=status.HTTP_200_OK)
def get_category(
    session: SessionDep,
    id: int
):
    post = session.get(Category, id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Couldn't find a category with id: {id}"
        )
    return post
        
@router.post("/", response_model=schemas.CategoryOut, status_code=status.HTTP_201_CREATED)
def post_category(
    session: SessionDep, category: schemas.CategoryBase
):
    query = select(Category)
    result = query.where(Category.name == category.name)
    post = session.exec(result)
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
    session.commit()
    session.refresh(new_category)
    
    if not new_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'invalid post input'
        )
    return new_category

@router.patch("/{id}", response_model=schemas.CategoryOut, status_code=status.HTTP_200_OK)
def update_category(id:int, session: SessionDep, category: schemas.CategoryUpdate):
    db_post = session.get(Category,id)
    if db_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"couldn't find a category with id: {id}")
    update_post = category.model_dump(exclude_unset=True)
    for field, value in update_post.items():
        setattr(db_post, field, value)
    db_post.updated_at = datetime.now()
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_category(id: int, session: SessionDep):
    db_post = session.get(Category,id)
    if db_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"couldn't find a category with id: {id}")
    session.delete(db_post)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)