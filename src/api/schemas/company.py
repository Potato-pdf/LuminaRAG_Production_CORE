"""
Pydantic schemas for companies.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    """Base company schema"""
    name: str
    slug: str


class CompanyCreate(BaseModel):
    """Company creation schema"""
    name: str
    slug: str
    max_documents: int = 100
    max_storage_gb: float = 5.0
    max_queries_per_month: int = 1000


class CompanyUpdate(BaseModel):
    """Company update schema"""
    name: Optional[str] = None
    max_documents: Optional[int] = None
    max_storage_gb: Optional[float] = None
    max_queries_per_month: Optional[int] = None
    is_active: Optional[bool] = None


class CompanyResponse(BaseModel):
    """Company response schema"""
    id: int
    name: str
    slug: str
    is_active: bool
    max_documents: int
    max_storage_gb: float
    max_queries_per_month: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompanyStats(BaseModel):
    """Company usage statistics"""
    document_count: int
    storage_used_gb: float
    storage_limit_gb: float
    document_limit: int
    storage_percentage: float
    document_percentage: float


class CompanyWithStats(CompanyResponse):
    """Company with usage statistics"""
    stats: CompanyStats
