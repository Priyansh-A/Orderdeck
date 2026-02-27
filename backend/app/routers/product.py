from .. import schemas, auth
from ..permissions import *
from ..models import Category, Product
from fastapi import Response, status, HTTPException, APIRouter, Depends, Request
from sqlalchemy.orm import selectinload
from sqlmodel import select, func
from ..database import SessionDep
from datetime import datetime
from typing import List, Optional
from time import timezone

router = APIRouter(
    prefix="/products",
    tags=['Products']
)

@router.get("/", response_model=List[schemas.ProductOut], status_code=status.HTTP_200_OK)
async def get_products(
    request: Request,
    session: SessionDep,
    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))
):
    query = select(Product).options(selectinload(Product.owner))
    result = await session.exec(query)
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
async def get_product(
    request: Request,
    session: SessionDep,
    id: int,
    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))
):
    query = select(Product).where(Product.id == id).options(selectinload(Product.owner))
    result = await session.exec(query)
    post = result.first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Couldn't find product with id: {id}"
        )
    base_url = str(request.base_url).rstrip('/')
    return schemas.ProductOut.from_orm_with_url(post,base_url)
        
@router.post("/", response_model=schemas.ProductBase, status_code=status.HTTP_201_CREATED)
async def post_product(
    request: Request,
    session: SessionDep, 
    product: schemas.ProductBase,
    current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.CREATE_MENU_ITEM]))
):
    query = select(Product)
    result = query.where(Product.name == product.name)
    post = await session.exec(result)
    existing = post.first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists"
        )
        
    category = await session.get(Category, product.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {product.category_id} does not exist"
        )
        
    new = Product(
        name = product.name,
        price = product.price,
        category_id = product.category_id,
        image_url=product.image_url
    )
    session.add(new)
    await session.commit()
    await session.refresh(new)
    
    await session.refresh(new, ["owner"])

    base_url = str(request.base_url).rstrip('/')
    return schemas.ProductOut.from_orm_with_url(new, base_url)

@router.patch("/{id}", response_model=schemas.ProductOut, status_code=status.HTTP_200_OK)
async def update_product(id:int,
                request: Request,
                session: SessionDep, 
                product: schemas.ProductUpdate,
                current_user:schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_MENU_ITEM]))
                ):
    db_product = await session.get(Product,id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"couldn't find a product with id: {id}")
    
    if product.category_id and product.category_id != db_product.category_id:
        category = await session.get(Category, product.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {product.category_id} does not exist"
            )
    
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db_product.updated_at = datetime.now(timezone.utc)
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)
    await session.refresh(db_product, ["owner"])
    
    base_url = str(request.base_url).rstrip('/')
    return schemas.ProductOut.from_orm_with_url(db_product, base_url)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: int, 
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.DELETE_MENU_ITEM]))
):
    db_product = await session.get(Product, id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Couldn't find a product with id: {id}"
        )
    await session.delete(db_product)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)