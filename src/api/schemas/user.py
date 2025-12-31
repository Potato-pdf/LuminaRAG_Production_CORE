"""
Pydantic schemas for users.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    password: str
    full_name: str
    company_id: int
    is_superuser: bool = False


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithCompany(UserResponse):
    """User response with company information"""
    company_name: str
    company_slug: str
