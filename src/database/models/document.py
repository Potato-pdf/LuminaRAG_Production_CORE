"""
Document model - Represents uploaded documents.
"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, BigInteger, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base
from src.database.base import BaseModel


class Document(Base, BaseModel):
    """
    Document model.
    Tracks uploaded documents and their metadata.
    """
    __tablename__ = "documents"

    # File Information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)  # Original name before sanitization
    s3_key = Column(String(500), unique=True, nullable=False, index=True)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt, etc.
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    
    # Privacy
    is_private = Column(Boolean, default=False, nullable=False, index=True)
    
    # Ownership
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Indexing Status
    indexed_at = Column(DateTime, nullable=True)
    index_status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    index_error = Column(String(500), nullable=True)
    
    # Additional Metadata (JSONB for flexibility)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="documents")
    uploaded_by_user = relationship("User", back_populates="uploaded_documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', company_id={self.company_id})>"

    def get_s3_url(self, bucket: str) -> str:
        """Get full S3 URL for the document"""
        return f"s3://{bucket}/{self.s3_key}"

    def mark_as_indexed(self):
        """Mark document as successfully indexed"""
        self.indexed_at = datetime.utcnow()
        self.index_status = "completed"
        self.index_error = None

    def mark_as_failed(self, error: str):
        """Mark document indexing as failed"""
        self.index_status = "failed"
        self.index_error = error

    def mark_for_reindex(self):
        """Mark document for re-indexing"""
        self.index_status = "pending"
        self.indexed_at = None
        self.index_error = None

    @property
    def is_indexed(self) -> bool:
        """Check if document is indexed"""
        return self.index_status == "completed"

    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return self.file_size / (1024 * 1024)
