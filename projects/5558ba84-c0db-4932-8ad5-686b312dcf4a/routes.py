from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from models import User, UserCreate, UserUpdate, Item, ItemCreate, ItemUpdate
from auth import get_current_user, fake_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

router = APIRouter()

# Define database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlalchemy.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database models
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)

class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("UserDB", back_populates="items")

Base.metadata.create_all(bind=engine)

# Define database functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define routes
@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = UserDB(username=user.username, email=user.email, full_name=user.full_name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/items/", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = db.query(ItemDB).filter(ItemDB.title == item.title).first()
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exists")
    db_item = ItemDB(title=item.title, description=item.description, owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/items/", response_model=List[Item])
def get_items(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    items = db.query(ItemDB).filter(ItemDB.owner_id == current_user.id).all()
    return items

@router.get("/users/me", response_model=User)
def get_current_user_me(current_user: dict = Depends(get_current_user)):
    return current_user
