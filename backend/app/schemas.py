from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from .permissions import UserRole
import enum

# ENUMS
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

# USER SCHEMAS
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "staff"
    disabled: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
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

# CATEGORY SCHEMAS
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None

class CategoryOut(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# PRODUCT SCHEMAS
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    image_url: Optional[str] = None
    is_available: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    image_full_url: Optional[str] = None
    category: Optional[CategoryOut] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_url(cls, product, base_url="http://localhost:8000"):
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id,
            image_url=product.image_url,
            is_available=product.is_available,
            created_at=product.created_at,
            updated_at=product.updated_at,
            image_full_url=f"{base_url}/assets/products/{product.image_url}" if product.image_url else None,
            category=product.category
        )

# TABLE SCHEMAS 
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
    occupied_by_party_id: Optional[str] = None
    occupied_by_customer: Optional[str] = None
    
    class Config:
        from_attributes = True

# CART SCHEMAS 
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)
    notes: Optional[str] = None

class CartItemCreate(CartItemBase):
    pass

class CartItemOut(CartItemBase):
    id: int
    unit_price: float
    subtotal: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CartBase(BaseModel):
    table_id: Optional[int] = None
    customer_name: Optional[str] = None
    notes: Optional[str] = None

class CartOut(CartBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[CartItemOut] = []
    subtotal: float = 0.0
    total_items: int = 0
    
    class Config:
        from_attributes = True

# ORDER SCHEMAS 
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
    customer_phone: Optional[str] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderOut(BaseModel):
    id: int
    order_number: str
    order_type: OrderType
    table_id: Optional[int] = None
    party_id: Optional[str] = None
    user_id: int
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    subtotal: float
    total_amount: float
    status: OrderStatus
    payment_status: PaymentStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemOut] = []
    payment: Optional["PaymentOut"] = None
    table: Optional[TableOut] = None
    
    class Config:
        from_attributes = True

# PAYMENT SCHEMAS 
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

#  CHECKOUT SCHEMA 
class CheckoutRequest(BaseModel):
    cart_id: int
    order_type: OrderType
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None

# Forward references
OrderOut.model_rebuild()