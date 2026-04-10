from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from sqlalchemy import Column, Boolean, Enum, TIMESTAMP, text, String, Float, Integer, JSON
from datetime import datetime, timezone
import enum
import json

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


# USER MODEL 
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False)
    email: str = Field(
        sa_column=Column(
            String, 
            unique=True, 
            nullable=False,
            index=True
        )
    )
    password: str = Field(nullable=False)
    role: str = Field(index=True, nullable=False, default="staff")
    disabled: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    
    # Relationships
    carts: List["Cart"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")


# CART MODEL 
class Cart(SQLModel, table=True):
    __tablename__ = "carts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    table_id: Optional[int] = Field(default=None, foreign_key="tables.id")
    customer_name: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc).replace(tzinfo=None),
            "nullable": True
        }
    )
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="carts")
    table: Optional["Table"] = Relationship(back_populates="carts")
    items: List["CartItem"] = Relationship(back_populates="cart")


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="carts.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(default=1, nullable=False)
    unit_price: float = Field(nullable=False)  
    subtotal: float = Field(nullable=False)    
    notes: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc).replace(tzinfo=None),
            "nullable": True
        }
    )
    
    # Relationships
    cart: Cart = Relationship(back_populates="items")
    product: Product = Relationship()


# CATEGORY MODEL 
class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc).replace(tzinfo=None),
            "nullable": True
        }
    )
    
    # Relationships
    products: List["Product"] = Relationship(back_populates="category")


# PRODUCT MODEL 
class Product(SQLModel, table=True):
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(nullable=False)
    image_url: Optional[str] = Field(default=None, max_length=500)
    is_available: bool = Field(default=True)
    category_id: int = Field(foreign_key="categories.id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc).replace(tzinfo=None),
            "nullable": True
        }
    )
    
    # Relationships
    category: Optional[Category] = Relationship(back_populates="products")
    order_items: List["OrderItem"] = Relationship(back_populates="product")
    cart_items: List[CartItem] = Relationship()


# TABLE MODEL 
class Table(SQLModel, table=True):
    __tablename__ = "tables"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    table_number: str = Field(index=True, unique=True, nullable=False)
    capacity: int = Field(nullable=False)
    status: TableStatus = Field(
        sa_column=Column(Enum(TableStatus), nullable=False, server_default='AVAILABLE')
    )
    is_active: bool = Field(
        default=True,
        sa_column=Column(
            Boolean, 
            nullable=False, 
            server_default=text('TRUE')
        )
    )
    occupied_by_party_id: Optional[str] = Field(default=None, index=True)
    occupied_by_customer: Optional[str] = Field(default=None, max_length=100)
    occupied_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc).replace(tzinfo=None),
            "nullable": True
        }
    )
    
    # Relationships
    orders: List["Order"] = Relationship(back_populates="table")
    carts: List[Cart] = Relationship(back_populates="table")


# ORDER MODEL 
class Order(SQLModel, table=True):
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: str = Field(index=True, unique=True, nullable=False)
    order_type: OrderType = Field(sa_column=Column(Enum(OrderType), nullable=False))
    table_id: Optional[int] = Field(default=None, foreign_key="tables.id")
    party_id: Optional[str] = Field(default=None, index=True)
    user_id: int = Field(foreign_key="users.id")
    customer_name: Optional[str] = Field(default=None, max_length=100)
    transaction_id: Optional[str] = Field(default=None, index=True)
    customer_phone: Optional[str] = Field(default=None, max_length=20)
    subtotal: float = Field(default=0.0)
    total_amount: float = Field(default=0.0)
    status: OrderStatus = Field(
        sa_column=Column(Enum(OrderStatus), nullable=False, server_default='PENDING')
    )
    payment_status: PaymentStatus = Field(
        sa_column=Column(Enum(PaymentStatus), nullable=False, server_default='PENDING')
    )
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc).replace(tzinfo=None),
            "nullable": True
        }
    )
    
    # Relationships
    table: Optional[Table] = Relationship(back_populates="orders")
    user: Optional[User] = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")
    payment: Optional["Payment"] = Relationship(back_populates="order")


# ORDER ITEM MODEL 
class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(default=1, nullable=False)
    unit_price: float = Field(nullable=False)
    subtotal: float = Field(nullable=False)
    notes: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    
    # Relationships
    order: Order = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="order_items")


# PAYMENT MODEL 
class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", unique=True)
    amount: float = Field(nullable=False)
    payment_method: PaymentMethod = Field(sa_column=Column(Enum(PaymentMethod), nullable=False))
    status: PaymentStatus = Field(
        sa_column=Column(Enum(PaymentStatus), nullable=False, server_default='PENDING')
    )
    transaction_id: Optional[str] = Field(default=None, max_length=100)
    payment_data: Optional[str] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    
    # Relationships
    order: Order = Relationship(back_populates="payment")