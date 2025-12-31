"""
Pydantic schemas for authentication.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    sub: str
    email: str
    company_id: int
    type: str


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    full_name: str
    company_name: str


class APIKeyCreate(BaseModel):
    """API key creation request"""
    name: str
    expires_in_days: Optional[int] = 365


class APIKeyResponse(BaseModel):
    """API key response (only time the key is shown)"""
    id: int
    name: str
    api_key: str  # Plain text key - only shown once
    expires_at: Optional[str]
    
    class Config:
        from_attributes = True


class APIKeyInfo(BaseModel):
    """API key information (without the actual key)"""
    id: int
    name: str
    is_active: bool
    expires_at: Optional[str]
    last_used_at: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True
