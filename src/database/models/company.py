"""
Company model - Represents a client company/organization.
"""
from sqlalchemy import Column, String, Integer, Boolean, Float
from sqlalchemy.orm import relationship
from src.database import Base
from src.database.base import BaseModel


class Company(Base, BaseModel):
    """
    Company/Organization model.
    Each company has its own isolated data and configuration.
    """
    __tablename__ = "companies"

    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Limits (for billing/quotas)
    max_documents = Column(Integer, default=100, nullable=False)
    max_storage_gb = Column(Float, default=5.0, nullable=False)
    max_queries_per_month = Column(Integer, default=1000, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="company", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="company", cascade="all, delete-orphan")
    config = relationship("CompanyConfig", back_populates="company", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    def check_document_limit(self, current_count: int) -> bool:
        """Check if company can add more documents"""
        return current_count < self.max_documents

    def check_storage_limit(self, current_gb: float) -> bool:
        """Check if company has storage available"""
        return current_gb < self.max_storage_gb

    def check_query_limit(self, current_count: int) -> bool:
        """Check if company can make more queries this month"""
        return current_count < self.max_queries_per_month
