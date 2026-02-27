from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from sqlalchemy import Column, Boolean, TIMESTAMP, text, String
from datetime import datetime, timezone

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
    owner: Optional[Category] = Relationship(back_populates="products")    