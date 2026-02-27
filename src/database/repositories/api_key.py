"""
API Key repository with specific queries for API key management.
"""
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models.api_key import APIKey
from src.database.repositories.base import BaseRepository


class APIKeyRepository(BaseRepository[APIKey]):
    """Repository for APIKey model with specific queries"""

    def __init__(self, db: Session):
        super().__init__(APIKey, db)

    def get_by_key(self, key: str) -> Optional[APIKey]:
        """
        Get API key by the actual key value.
        
        Args:
            key: API key string
            
        Returns:
            APIKey instance or None if not found
        """
        key_hash = APIKey.hash_key(key)
        
        return self.db.query(APIKey).filter(
            APIKey.key_hash == key_hash,
            APIKey.is_deleted == False
        ).first()

    def verify_and_update(self, key: str) -> Optional[APIKey]:
        """
        Verify API key and update last_used_at timestamp.
        
        Args:
            key: API key string
            
        Returns:
            APIKey instance if valid, None otherwise
        """
        api_key = self.get_by_key(key)
        
        if not api_key:
            return None
        
        if not api_key.is_valid():
            return None
        
        # Update last used timestamp
        api_key.mark_used()
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key

    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100):
        """
        Get all API keys for a company.
        
        Args:
            company_id: Company ID
            skip: Pagination offset
            limit: Maximum results
            
        Returns:
            List of API keys
        """
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"company_id": company_id}
        )

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        """
        Get all API keys for a user.
        
        Args:
            user_id: User ID
            skip: Pagination offset
            limit: Maximum results
            
        Returns:
            List of API keys
        """
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"user_id": user_id}
        )

    def create_api_key(
        self,
        name: str,
        company_id: int,
        user_id: int,
        expires_in_days: Optional[int] = 365
    ) -> tuple[APIKey, str]:
        """
        Create a new API key.
        
        Args:
            name: Descriptive name for the key
            company_id: Company ID
            user_id: User ID who created the key
            expires_in_days: Number of days until expiration (None for no expiration)
            
        Returns:
            Tuple of (APIKey instance, plain text key)
            Note: The plain text key is only returned once and cannot be retrieved later
        """
        # Generate new key
        plain_key = APIKey.generate_key()
        key_hash = APIKey.hash_key(plain_key)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key record
        api_key = self.create({
            "key_hash": key_hash,
            "name": name,
            "company_id": company_id,
            "user_id": user_id,
            "expires_at": expires_at,
            "is_active": True
        })
        
        return api_key, plain_key

    def revoke(self, key_id: int) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id: API key ID
            
        Returns:
            True if revoked successfully, False otherwise
        """
        api_key = self.get(key_id)
        
        if not api_key:
            return False
        
        api_key.revoke()
        self.db.commit()
        
        return True

    def revoke_by_key(self, key: str) -> bool:
        """
        Revoke an API key by the key value.
        
        Args:
            key: API key string
            
        Returns:
            True if revoked successfully, False otherwise
        """
        api_key = self.get_by_key(key)
        
        if not api_key:
            return False
        
        api_key.revoke()
        self.db.commit()
        
        return True
