"""
Pydantic schemas for documents.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class DocumentBase(BaseModel):
    """Base document schema"""
    filename: str
    is_private: bool = False


class DocumentCreate(BaseModel):
    """Document creation schema (for multipart upload)"""
    is_private: bool = False
    metadata: Optional[Dict[str, Any]] = None


class DocumentUpdate(BaseModel):
    """Document update schema"""
    filename: Optional[str] = None
    is_private: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    """Document response schema"""
    id: int
    filename: str
    original_filename: str
    s3_key: str
    file_type: str
    file_size: int
    file_size_mb: float
    is_private: bool
    company_id: int
    uploaded_by: int
    index_status: str
    indexed_at: Optional[datetime]
    created_at: datetime
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """Paginated document list"""
    total: int
    documents: list[DocumentResponse]
    skip: int
    limit: int
