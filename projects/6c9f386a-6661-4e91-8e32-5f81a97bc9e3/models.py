from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from passlib.context import CryptContext

class User(BaseModel):
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username chosen by the user")
    email: str = Field(..., description="Email address of the user")
    full_name: Optional[str] = Field(None, description="Full name of the user")
    disabled: bool = Field(False, description="Whether the user is disabled or not")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the user was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the user was last updated")
    hashed_password: str = Field(..., description="Hashed password of the user")

    def get_password_hash(self, password):
        pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")
        return pwd_context.hash(password)

    def verify_password(self, plain_password):
        pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")
        return pwd_context.verify(plain_password, self.hashed_password)


class Item(BaseModel):
    id: int = Field(..., description="Item ID")
    title: str = Field(..., description="Title of the item")
    description: Optional[str] = Field(None, description="Description of the item")
    owner_id: int = Field(..., description="ID of the user who owns the item")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the item was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the item was last updated")
