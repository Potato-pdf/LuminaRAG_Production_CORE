"""
User repository with specific queries for user management.
"""
from typing import Optional
from sqlalchemy.orm import Session
from src.database.models.user import User
from src.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model with specific queries"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            User instance if authentication successful, None otherwise
        """
        user = self.get_by_email(email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not user.verify_password(password):
            return None
        
        return user

    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100):
        """
        Get all users belonging to a company.
        
        Args:
            company_id: Company ID
            skip: Pagination offset
            limit: Maximum results
            
        Returns:
            List of users
        """
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"company_id": company_id}
        )

    def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        company_id: int,
        is_superuser: bool = False
    ) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            email: User email
            password: Plain text password (will be hashed)
            full_name: User's full name
            company_id: Company ID
            is_superuser: Whether user is a superuser
            
        Returns:
            Created user instance
        """
        hashed_password = User.hash_password(password)
        
        return self.create({
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "company_id": company_id,
            "is_superuser": is_superuser,
            "is_active": True
        })

    def update_password(self, user_id: int, new_password: str) -> Optional[User]:
        """
        Update user password.
        
        Args:
            user_id: User ID
            new_password: New plain text password (will be hashed)
            
        Returns:
            Updated user or None if not found
        """
        user = self.get(user_id)
        
        if not user:
            return None
        
        user.set_password(new_password)
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def activate(self, user_id: int) -> Optional[User]:
        """Activate a user"""
        return self.update(self.get(user_id), {"is_active": True})

    def deactivate(self, user_id: int) -> Optional[User]:
        """Deactivate a user"""
        return self.update(self.get(user_id), {"is_active": False})
