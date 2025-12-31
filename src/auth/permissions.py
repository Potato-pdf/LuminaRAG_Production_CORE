"""
Permission checking using Strategy Pattern.
"""
from abc import ABC, abstractmethod
from typing import Optional
from fastapi import HTTPException, status

from src.database.models.user import User
from src.database.models.company import Company
from src.database.models.document import Document


class PermissionChecker(ABC):
    """
    Abstract base class for permission checkers.
    Implements Strategy Pattern for different permission types.
    """

    @abstractmethod
    def check(self, user: User, resource: any) -> bool:
        """
        Check if user has permission for the resource.
        
        Args:
            user: User to check
            resource: Resource to check permission for
            
        Returns:
            True if user has permission, False otherwise
        """
        pass

    def check_or_raise(self, user: User, resource: any):
        """
        Check permission and raise exception if denied.
        
        Args:
            user: User to check
            resource: Resource to check permission for
            
        Raises:
            HTTPException: If permission denied
        """
        if not self.check(user, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )


class CompanyAccessChecker(PermissionChecker):
    """Check if user has access to a company"""

    def check(self, user: User, company: Company) -> bool:
        """
        Check if user can access the company.
        Superusers can access all companies.
        Regular users can only access their own company.
        """
        if user.is_superuser:
            return True
        
        return user.company_id == company.id


class DocumentAccessChecker(PermissionChecker):
    """Check if user has access to a document"""

    def check(self, user: User, document: Document) -> bool:
        """
        Check if user can access the document.
        Superusers can access all documents.
        Regular users can only access documents from their company.
        """
        if user.is_superuser:
            return True
        
        return user.company_id == document.company_id


class DocumentEditChecker(PermissionChecker):
    """Check if user can edit a document"""

    def check(self, user: User, document: Document) -> bool:
        """
        Check if user can edit the document.
        Superusers can edit all documents.
        Regular users can only edit documents they uploaded.
        """
        if user.is_superuser:
            return True
        
        # Must be from same company
        if user.company_id != document.company_id:
            return False
        
        # Must be the uploader
        return user.id == document.uploaded_by


class AdminPermissionChecker(PermissionChecker):
    """Check if user is admin/superuser"""

    def check(self, user: User, resource: any = None) -> bool:
        """Check if user is superuser"""
        return user.is_superuser


# Singleton instances
company_access = CompanyAccessChecker()
document_access = DocumentAccessChecker()
document_edit = DocumentEditChecker()
admin_permission = AdminPermissionChecker()
