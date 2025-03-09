# backend/schemas.py
from pydantic import BaseModel
from datetime import date
from typing import Optional, List
import json

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

# ✅ Exercise Schema
class ExerciseSchema(BaseModel):
    id: Optional[int]
    name: str
    description: str
    toughness: str
    media_url: Optional[str]
    tags: List[str]  # Ensure it's a list, JSON field should be converted
    suggested_reps: Optional[int]


class Config:
    from_attributes = True  # ✅ Updated for Pydantic V2


class LoginRequest(BaseModel):
    email: str
    password: str