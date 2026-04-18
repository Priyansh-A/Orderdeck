from .. import schemas, auth
from ..permissions import *
from ..models import Category, Product
from fastapi import Response, status, HTTPException, APIRouter, Depends, Request, UploadFile, File, Form
from sqlalchemy.orm import selectinload
from sqlmodel import select
from ..database import SessionDep
from datetime import datetime, timezone
from typing import List, Optional
import shutil
import os
from pathlib import Path
import uuid

router = APIRouter(
    prefix="/products",
    tags=['Products']
)

UPLOAD_DIR = Path(__file__).parent.parent / "assets" / "products"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_uploaded_file(uploaded_file: UploadFile, keep_original_name: bool = False) -> str:
    """Save uploaded file"""
    if keep_original_name:
        filename = uploaded_file.filename
        filename = os.path.basename(filename)
    else:
        file_extension = Path(uploaded_file.filename).suffix
        filename = f"{uuid.uuid4().hex}{file_extension}"
    
    file_path = UPLOAD_DIR / filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    
    return filename

def delete_old_image(filename: str):
    """Delete old image file if it exists"""
    if filename and '/' not in filename:
        old_image_path = UPLOAD_DIR / filename
        if old_image_path.exists():
            old_image_path.unlink()


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
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.CREATE_MENU_ITEM])),
    name: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    description: Optional[str] = Form(None),
    is_available: bool = Form(True),
    image_url: Optional[str] = Form(None), 
    image: Optional[UploadFile] = File(None),
    keep_original_name: bool = Form(False) 
):
    """Add a product with optional image upload"""
    
    query = select(Product).where(Product.name == name)
    result = await session.exec(query)
    existing = result.first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this name already exists"
        )
    
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {category_id} does not exist"
        )
    
    final_image_url = image_url
    if image:
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only JPEG, JPG, PNG, GIF, and WEBP are allowed."
            )
        
        file_size = 0
        chunk_size = 1024
        while chunk := await image.read(chunk_size):
            file_size += len(chunk)
            if file_size > 5 * 1024 * 1024: 
                raise HTTPException(
                    status_code=400,
                    detail="File too large. Maximum size is 5MB."
                )
        await image.seek(0) 
        
        final_image_url = save_uploaded_file(image, keep_original_name=keep_original_name)
    elif image_url:
        final_image_url = image_url
    
    new_product = Product(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        image_url=final_image_url,
        is_available=is_available
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
    current_user: schemas.UserInDb = Depends(auth.require_permissions([Permission.UPDATE_MENU_ITEM])),
    name: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    is_available: Optional[bool] = Form(None),
    image_url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    keep_original_name: bool = Form(False)
):
    """Update product"""
    
    db_product = await session.get(Product, id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Couldn't find a product with id: {id}")
    
    if category_id and category_id != db_product.category_id:
        category = await session.get(Category, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {category_id} does not exist"
            )
        db_product.category_id = category_id
    
    if image:
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only JPEG, JPG, PNG, GIF, and WEBP are allowed."
            )
        
        file_size = 0
        chunk_size = 1024
        while chunk := await image.read(chunk_size):
            file_size += len(chunk)
            if file_size > 5 * 1024 * 1024: 
                raise HTTPException(
                    status_code=400,
                    detail="File too large. Maximum size is 5MB."
                )
        await image.seek(0)
        
        if db_product.image_url:
            delete_old_image(db_product.image_url)
        
        db_product.image_url = save_uploaded_file(image, keep_original_name=keep_original_name)
    elif image_url is not None:
        if db_product.image_url and not image_url:
            delete_old_image(db_product.image_url)
        db_product.image_url = image_url
    
    if name is not None:
        db_product.name = name
    if price is not None:
        db_product.price = price
    if description is not None:
        db_product.description = description
    if is_available is not None:
        db_product.is_available = is_available
    
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
    """Remove a product and its associated image"""
    db_product = await session.get(Product, id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Couldn't find a product with id: {id}"
        )
    
    if db_product.image_url:
        delete_old_image(db_product.image_url)
    
    await session.delete(db_product)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)