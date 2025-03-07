# backend/schemas.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str
    password: str
    dob: date
    weight: int
    height: int
    gender: str
    role: Optional[str] = "user"  # Default role is 'user'

from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str
