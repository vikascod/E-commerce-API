from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    email: str
    full_name: str
    address: str
    phone: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    is_active: bool
    created_at: Optional[datetime]
    class Config:
        orm_mode=True


class ProductBase(BaseModel):
    name: str
    price: int
    description: Optional[str]
    is_sale: Optional[bool]


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id:int
    created_at: Optional[datetime]
    class Config:
        orm_mode=True


class OrderBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    id: int
    total_price: int
    is_confirmed: Optional[bool]
    created_at: Optional[datetime]
    user: Optional[User]
    product: Optional[Product]
    class Config:
        orm_mode=True


class CartBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class CartCreate(CartBase):
    pass


class Cart(CartBase):
    id: int
    user: Optional[User]
    product: Optional[Product]
    quantity: int
    class Config:
        orm_mode=True