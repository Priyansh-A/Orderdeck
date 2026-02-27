from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Annotated, List
from sqlmodel import SQLModel
from .permissions import UserRole

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.STAFF
    disabled: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    disabled: Optional[bool] = None

class UserOut(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserInDb(UserOut):
    password: str

class TokenData(BaseModel):
    id: int
    role: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    
class CategoryOut(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class CategoryUpdate(CategoryBase):
    pass

# Product Schemas
class ProductBase(BaseModel):
    name: str
    price: int
    category_id: int
    image_url: Optional[str] = None
    
class ProductUpdate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] 
    image_full_url: Optional[str] = None
    owner: CategoryOut
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_with_url(cls, product, base_url="http://localhost:8000"):
        """Convert ORM model to response with full image URL"""
        product_dict = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "category_id": product.category_id,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "image_url": product.image_url,
            "image_full_url": f"{base_url}/assets/products/{product.image_url}" if product.image_url else None,
            "owner": product.owner
        }
        return cls(**product_dict)