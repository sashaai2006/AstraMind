from fastapi import Depends, FastAPI
from pydantic import BaseModel
from auth import create_access_token, verify_password
from models import User
from typing import List

app = FastAPI()

# Define a function to get user by username
async def get_user_by_username(username: str):
    # Replace this with your actual database query
    # For demonstration purposes, assume we have a list of users
    users = [
        User(id=1, username="user1", email="user1@example.com", full_name="User 1", disabled=False, created_at="2022-01-01", updated_at="2022-01-01", hashed_password="hashed_password1"),
        User(id=2, username="user2", email="user2@example.com", full_name="User 2", disabled=False, created_at="2022-01-01", updated_at="2022-01-01", hashed_password="hashed_password2")
    ]
    for user in users:
        if user.username == username:
            return user
    return None
