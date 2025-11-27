from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreateSchema(BaseModel):
    email: EmailStr
    password_hash: str
    full_name: Optional[str] = None

class UserResponseSchema(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None
    full_name: Optional[str] = None
