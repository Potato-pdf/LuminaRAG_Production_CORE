"""
Document repository with specific queries for document management.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.models.document import Document
from src.database.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document model with specific queries"""

    def __init__(self, db: Session):
        super().__init__(Document, db)

    def get_by_s3_key(self, s3_key: str) -> Optional[Document]:
        """
        Get document by S3 key.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Document instance or None if not found
        """
        return self.db.query(Document).filter(
            Document.s3_key == s3_key,
            Document.is_deleted == False
        ).first()

    def get_by_company(
        self,
        company_id: int,
        is_private: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """
        Get documents for a company, optionally filtered by privacy.
        
        Args:
            company_id: Company ID
            is_private: Filter by privacy (None = all documents)
            skip: Pagination offset
            limit: Maximum results
            
        Returns:
            List of documents
        """
        query = self.db.query(Document).filter(
            Document.company_id == company_id,
            Document.is_deleted == False
        )
        
        if is_private is not None:
            query = query.filter(Document.is_private == is_private)
        
        return query.offset(skip).limit(limit).all()

    def get_pending_indexing(self, limit: int = 10) -> List[Document]:
        """
        Get documents pending indexing.
        
        Args:
            limit: Maximum results
            
        Returns:
            List of documents with pending status
        """
        return self.db.query(Document).filter(
            Document.index_status == "pending",
            Document.is_deleted == False
        ).limit(limit).all()

    def create_document(
        self,
        filename: str,
        original_filename: str,
        s3_key: str,
        file_type: str,
        file_size: int,
        is_private: bool,
        company_id: int,
        uploaded_by: int,
        metadata: Optional[dict] = None
    ) -> Document:
        """
        Create a new document record.
        
        Args:
            filename: Sanitized filename
            original_filename: Original filename from upload
            s3_key: S3 object key
            file_type: File extension/type
            file_size: File size in bytes
            is_private: Whether document is private
            company_id: Company ID
            uploaded_by: User ID who uploaded
            metadata: Additional metadata
            
        Returns:
            Created document instance
        """
        return self.create({
            "filename": filename,
            "original_filename": original_filename,
            "s3_key": s3_key,
            "file_type": file_type,
            "file_size": file_size,
            "is_private": is_private,
            "company_id": company_id,
            "uploaded_by": uploaded_by,
            "metadata": metadata or {},
            "index_status": "pending"
        })

    def mark_for_reindex(self, document_id: int) -> Optional[Document]:
        """
        Mark document for re-indexing.
        
        Args:
            document_id: Document ID
            
        Returns:
            Updated document or None if not found
        """
        document = self.get(document_id)
        
        if not document:
            return None
        
        document.mark_for_reindex()
        self.db.commit()
        self.db.refresh(document)
        
        return document

    def mark_as_indexed(self, document_id: int) -> Optional[Document]:
        """
        Mark document as successfully indexed.
        
        Args:
            document_id: Document ID
            
        Returns:
            Updated document or None if not found
        """
        document = self.get(document_id)
        
        if not document:
            return None
        
        document.mark_as_indexed()
        self.db.commit()
        self.db.refresh(document)
        
        return document

    def mark_as_failed(self, document_id: int, error: str) -> Optional[Document]:
        """
        Mark document indexing as failed.
        
        Args:
            document_id: Document ID
            error: Error message
            
        Returns:
            Updated document or None if not found
        """
        document = self.get(document_id)
        
        if not document:
            return None
        
        document.mark_as_failed(error)
        self.db.commit()
        self.db.refresh(document)
        
        return document

    def update_privacy(self, document_id: int, is_private: bool) -> Optional[Document]:
        """
        Update document privacy setting.
        
        Args:
            document_id: Document ID
            is_private: New privacy setting
            
        Returns:
            Updated document or None if not found
        """
        document = self.get(document_id)
        
        if not document:
            return None
        
        # Mark for re-indexing when privacy changes
        document.is_private = is_private
        document.mark_for_reindex()
        
        self.db.commit()
        self.db.refresh(document)
        
        return document
