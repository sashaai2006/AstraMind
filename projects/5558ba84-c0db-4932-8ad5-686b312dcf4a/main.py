from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from jose import jwt
from datetime import datetime, timedelta
import sqlite3
import os

# Define the FastAPI application
app = FastAPI()

# Define the Pydantic schema for user authentication
class User(BaseModel):
    username: str
    password: str

# Define the Pydantic schema for JWT token
class Token(BaseModel):
    access_token: str
    token_type: str

# Define the SQLite database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlalchemy.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the user model
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Define the JWT secret key
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Define the authentication function
def authenticate_user(username: str, password: str):
    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        return False
    if not user.password == password:
        return False
    return user

# Define the token generation function
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Define the JWT authentication function
def get_current_user(token: str = Depends()):
    # Implement JWT authentication logic here
    return token

# Define the route for user registration
@app.post("/register")
def register_user(user: User):
    db = SessionLocal()
    user_db = db.query(UserDB).filter(UserDB.username == user.username).first()
    if user_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = UserDB(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.close()
    return JSONResponse(content={"message": "User created successfully"}, status_code=201)

# Define the route for user login
@app.post("/login")
def login_user(user: User):
    user_db = authenticate_user(user.username, user.password)
    if not user_db:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"}, status_code=200)

# Define the route for protected endpoint
@app.get("/protected")
def read_protected(current_user: str = Depends(get_current_user)):
    return JSONResponse(content={"message": f"Hello, {current_user}"}, status_code=200)
