from .. import schemas
from ..models import Category, Product
from fastapi import Response, status, HTTPException, APIRouter, Depends, Request
from sqlalchemy.orm import selectinload
from sqlmodel import select, func
from ..database import SessionDep
from datetime import datetime
from typing import List, Optional

router = APIRouter(
    prefix="/products",
    tags=['Products']
)

@router.get("/", response_model=List[schemas.ProductOut], status_code=status.HTTP_200_OK)
def get_products(
    request: Request,
    session: SessionDep,
):
    query = select(Product).options(selectinload(Product.owner))
    result = session.exec(query)
    posts = result.all()
    
    base_url = str(request.base_url).rstrip('/')

    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Couldn't find any products"
        )

    return [
        schemas.ProductOut.from_orm_with_url(post,base_url)
        for post in posts
    ]

@router.get("/{id}", response_model=schemas.ProductOut, status_code=status.HTTP_200_OK)
def get_product(
    request: Request,
    session: SessionDep,
    id: int
):
    query = select(Product).where(Product.id == id).options(selectinload(Product.owner))
    result = session.exec(query)
    post = result.first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Couldn't find product with id: {id}"
        )
    base_url = str(request.base_url).rstrip('/')
    return schemas.ProductOut.from_orm_with_url(post,base_url)
        
@router.post("/", response_model=schemas.ProductBase, status_code=status.HTTP_201_CREATED)
def post_product(
    request: Request,
    session: SessionDep, 
    product: schemas.ProductBase
):
    query = select(Product)
    result = query.where(Product.name == product.name)
    post = session.exec(result)
    existing = post.first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists"
        )
    new = Product(
        name = product.name,
        price = product.price,
        category_id = product.category_id,
        image_url=product.image_url
    )
    session.add(new)
    session.commit()
    session.refresh(new)
    
    if not new:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'invalid post input'
        )
    base_url = str(request.base_url).rstrip('/')
    return schemas.ProductOut.from_orm_with_url(new, base_url)

@router.patch("/{id}", response_model=schemas.ProductBase, status_code=status.HTTP_200_OK)
def update_product(id:int, session: SessionDep, product: schemas.ProductUpdate):
    db_post = session.get(Product,id)
    if db_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"couldn't find a product with id: {id}")
    update_post = product.model_dump(exclude_unset=True)
    for field, value in update_post.items():
        setattr(db_post, field, value)
    db_post.updated_at = datetime.now()
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, session: SessionDep):
    db_post = session.get(Product,id)
    if db_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"couldn't find a product with id: {id}")
    session.delete(db_post)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)