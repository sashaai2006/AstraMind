from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

Base = declarative_base()

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class Item(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    owner_id: int

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    full_name = Column(String)
    disabled = Column(Boolean)
    created_at = Column(String)
    updated_at = Column(String)
    password = Column(String)

    items = relationship("ItemDB", back_populates="owner")

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(String)
    updated_at = Column(String)

    owner = relationship("UserDB", back_populates="items")

pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

def get_password_hash(password):
    return pwd_context.hash(password)
