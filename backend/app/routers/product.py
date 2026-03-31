from .. import schemas, auth
from ..permissions import *
from ..models import Category, Product
from fastapi import Response, status, HTTPException, APIRouter, Depends, Request
from sqlalchemy.orm import selectinload
from sqlmodel import select
from ..database import SessionDep
from datetime import datetime, timezone
from typing import List

router = APIRouter(
    prefix="/products",
    tags=['Products']
)

@router.get("/", response_model=List[schemas.ProductOut], status_code=status.HTTP_200_OK)
async def get_products(
    request: Request,
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))
):
    """Get products"""
    query = select(Product).options(selectinload(Product.category))
    result = await session.exec(query)
    products = result.all()
    
    base_url = str(request.base_url).rstrip('/')
    
    if not products:
        return []
    
    return [
        schemas.ProductOut.from_orm_with_url(product, base_url)
        for product in products
    ]

@router.get("/available", response_model=List[schemas.ProductOut], status_code=status.HTTP_200_OK)
async def get_available_products(
    request: Request,
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))
):
    """Get available Products"""
    query = select(Product).where(Product.is_available == True).options(selectinload(Product.category))
    result = await session.exec(query)
    products = result.all()
    
    base_url = str(request.base_url).rstrip('/')
    
    return [
        schemas.ProductOut.from_orm_with_url(product, base_url)
        for product in products
    ]

@router.get("/{id}", response_model=schemas.ProductOut, status_code=status.HTTP_200_OK)
async def get_product(
    request: Request,
    session: SessionDep,
    id: int,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.VIEW_MENU]))
):
    """Get specific product with Id"""
    query = select(Product).where(Product.id == id).options(selectinload(Product.category))
    result = await session.exec(query)
    product = result.first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Couldn't find product with id: {id}"
        )
    
    base_url = str(request.base_url).rstrip('/')
    return schemas.ProductOut.from_orm_with_url(product, base_url)
        
@router.post("/", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: Request,
    session: SessionDep, 
    product: schemas.ProductCreate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CREATE_MENU_ITEM]))
):
    """Add a product"""
    query = select(Product).where(Product.name == product.name)
    result = await session.exec(query)
    existing = result.first()
    
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
        
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        category_id=product.category_id,
        image_url=product.image_url,
        is_available=product.is_available
    )
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    await session.refresh(new_product, ["category"])
    
    base_url = str(request.base_url).rstrip('/')
    return schemas.ProductOut.from_orm_with_url(new_product, base_url)

@router.patch("/{id}", response_model=schemas.ProductOut, status_code=status.HTTP_200_OK)
async def update_product(
    id: int,
    request: Request,
    session: SessionDep, 
    product: schemas.ProductUpdate,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_MENU_ITEM]))
):
    """Update product info"""
    db_product = await session.get(Product, id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Couldn't find a product with id: {id}")
    
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
    
    db_product.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)
    await session.refresh(db_product, ["category"])
    
    base_url = str(request.base_url).rstrip('/')
    return schemas.ProductOut.from_orm_with_url(db_product, base_url)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: int, 
    session: SessionDep,
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.DELETE_MENU_ITEM]))
):
    """Remove a product"""
    db_product = await session.get(Product, id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Couldn't find a product with id: {id}"
        )
    await session.delete(db_product)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)