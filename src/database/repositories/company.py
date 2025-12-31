"""
Company repository with specific queries for company management.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database.models.company import Company
from src.database.models.document import Document
from src.database.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Repository for Company model with specific queries"""

    def __init__(self, db: Session):
        super().__init__(Company, db)

    def get_by_slug(self, slug: str) -> Optional[Company]:
        """
        Get company by slug.
        
        Args:
            slug: Company slug
            
        Returns:
            Company instance or None if not found
        """
        return self.db.query(Company).filter(
            Company.slug == slug,
            Company.is_deleted == False
        ).first()

    def get_by_name(self, name: str) -> Optional[Company]:
        """
        Get company by name.
        
        Args:
            name: Company name
            
        Returns:
            Company instance or None if not found
        """
        return self.db.query(Company).filter(
            Company.name == name,
            Company.is_deleted == False
        ).first()

    def get_with_stats(self, company_id: int) -> Optional[dict]:
        """
        Get company with usage statistics.
        
        Args:
            company_id: Company ID
            
        Returns:
            Dictionary with company and stats or None if not found
        """
        company = self.get(company_id)
        
        if not company:
            return None
        
        # Count documents
        doc_count = self.db.query(func.count(Document.id)).filter(
            Document.company_id == company_id,
            Document.is_deleted == False
        ).scalar()
        
        # Calculate total storage (in GB)
        total_storage = self.db.query(func.sum(Document.file_size)).filter(
            Document.company_id == company_id,
            Document.is_deleted == False
        ).scalar() or 0
        
        total_storage_gb = total_storage / (1024 ** 3)  # Convert bytes to GB
        
        return {
            "company": company,
            "stats": {
                "document_count": doc_count,
                "storage_used_gb": round(total_storage_gb, 2),
                "storage_limit_gb": company.max_storage_gb,
                "document_limit": company.max_documents,
                "storage_percentage": round((total_storage_gb / company.max_storage_gb) * 100, 2) if company.max_storage_gb > 0 else 0,
                "document_percentage": round((doc_count / company.max_documents) * 100, 2) if company.max_documents > 0 else 0
            }
        }

    def create_company(
        self,
        name: str,
        slug: str,
        max_documents: int = 100,
        max_storage_gb: float = 5.0,
        max_queries_per_month: int = 1000
    ) -> Company:
        """
        Create a new company.
        
        Args:
            name: Company name
            slug: Company slug (URL-friendly)
            max_documents: Maximum number of documents
            max_storage_gb: Maximum storage in GB
            max_queries_per_month: Maximum queries per month
            
        Returns:
            Created company instance
        """
        return self.create({
            "name": name,
            "slug": slug,
            "max_documents": max_documents,
            "max_storage_gb": max_storage_gb,
            "max_queries_per_month": max_queries_per_month,
            "is_active": True
        })

    def activate(self, company_id: int) -> Optional[Company]:
        """Activate a company"""
        company = self.get(company_id)
        if company:
            return self.update(company, {"is_active": True})
        return None

    def deactivate(self, company_id: int) -> Optional[Company]:
        """Deactivate a company"""
        company = self.get(company_id)
        if company:
            return self.update(company, {"is_active": False})
        return None
