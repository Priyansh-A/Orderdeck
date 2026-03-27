from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Annotated, List
from sqlmodel import SQLModel, Enum
from .permissions import UserRole
import enum

class TableStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"

class OrderType(str, enum.Enum):
    DINE_IN = "dine_in"
    TAKEAWAY = "takeaway"
    
class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    ONLINE = "online"

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
    
    
class TableBase(BaseModel):
    table_number: str
    capacity: int

class TableCreate(TableBase):
    status: TableStatus = TableStatus.AVAILABLE

class TableUpdate(BaseModel):
    table_number: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[TableStatus] = None
    is_active: Optional[bool] = None

class TableStatusUpdate(BaseModel):
    status: TableStatus

class TableOut(TableBase):
    id: int
    status: TableStatus
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    active_order_count: Optional[int] = 0
    active_orders: Optional[List] = []
    
    class Config:
        from_attributes = True
        
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)
    notes: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id: int
    unit_price: float
    subtotal: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    order_type: OrderType
    table_id: Optional[int] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    customer_name: Optional[str] = None

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderOut(BaseModel):
    id: int
    order_number: str
    order_type: OrderType
    table_id: Optional[int]
    party_id: Optional[str]  # Add this
    user_id: int
    customer_name: Optional[str]
    subtotal: float
    total_amount: float
    status: OrderStatus
    payment_status: PaymentStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[OrderItemOut] = []
    payment: Optional["PaymentOut"] = None
    
    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    order_id: int
    payment_method: PaymentMethod
    transaction_id: Optional[str] = None
    payment_data: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int
    amount: float
    status: PaymentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# Forward reference for OrderOut
OrderOut.model_rebuild()