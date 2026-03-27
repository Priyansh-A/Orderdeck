from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from sqlalchemy import Column, Boolean, Enum, TIMESTAMP, text, String
from datetime import datetime, timezone
import enum

class TableStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"

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
    created_at: datetime = Field(
        default_factory=lambda:datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    disabled: bool = Field(
        default=False,
        sa_column=Column(
            Boolean, 
            nullable=False, 
            server_default=text('FALSE')
        )
    )
    role: str = Field(index=True, nullable=False)
    
    
class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda:datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    updated_at: datetime | None = Field(
    default=None,
    sa_column_kwargs={
        "onupdate": lambda: datetime.now(timezone.utc),
        "nullable": True
        }
    )
    
    # relationships
    products: List["Product"] = Relationship(back_populates="owner")
    
class Product(SQLModel, table=True):
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    image_url: Optional[str] = Field(default=None, max_length=500)
    price: int = Field(nullable=False)
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
        "onupdate": lambda: datetime.now(timezone.utc),
        "nullable": True
        }
    )
    category_id: int = Field(foreign_key="categories.id")
    # relationships
    category: Optional[Category] = Relationship(back_populates="products")


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
            "onupdate": lambda: datetime.now(timezone.utc),
            "nullable": True
        }
    )
    # relationships
    orders: List["Order"] = Relationship(back_populates="table")
    
class Order(SQLModel, table=True):
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: str = Field(index=True, unique=True, nullable=False)
    order_type: OrderType = Field(sa_column=Column(Enum(OrderType), nullable=False))
    table_id: Optional[int] = Field(default=None, foreign_key="tables.id")
    user_id: int = Field(foreign_key="users.id") 
    customer_name: Optional[str] = Field(default=None, max_length=100)
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
            "onupdate": lambda: datetime.now(timezone.utc),
            "nullable": True
        }
    )


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(default=1, nullable=False)
    unit_price: float = Field(nullable=False)
    subtotal: float = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True), 
            nullable=False, 
            server_default=text('CURRENT_TIMESTAMP')
        )
    )
    
    
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