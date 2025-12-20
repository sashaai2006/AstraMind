from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from typing import List
import uvicorn
import jwt
import datetime

# Define the database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlalchemy.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the user model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Define the Pydantic schema for user data validation
class UserSchema(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

# Define the FastAPI application instance
app = FastAPI()

# Define the JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define the token endpoint
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate the user credentials
    user = SessionLocal().query(User).filter(User.username == form_data.username).first()
    if not user or not user.hashed_password == form_data.password:
        return {
            "error": "Invalid username or password"
        }

    # Generate the JWT token
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(),
        "sub": user.id
    }
    token = jwt.encode(payload, "secret_key", algorithm="HS256")

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# Define the protected endpoint
@app.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    try:
        # Verify the JWT token
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        user_id = payload["sub"]
        user = SessionLocal().query(User).filter(User.id == user_id).first()
        return {
            "message": f"Hello, {user.username}!"
        }
    except jwt.ExpiredSignatureError:
        return {
            "error": "Token has expired"
        }
    except jwt.InvalidTokenError:
        return {
            "error": "Invalid token"
        }

# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
