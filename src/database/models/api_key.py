"""
API Key model - For API authentication.
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base
from src.database.base import BaseModel


class APIKey(Base, BaseModel):
    """
    API Key model for programmatic access.
    Keys are hashed before storage for security.
    """
    __tablename__ = "api_keys"

    # Key Information
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)  # Descriptive name for the key
    
    # Ownership
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Status and Expiration
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="api_keys")
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<APIKey(id={self.id}, name='{self.name}', company_id={self.company_id})>"

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new API key.
        Format: lum_<32_random_chars>
        """
        random_part = secrets.token_urlsafe(32)
        return f"lum_{random_part}"

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()

    def verify_key(self, key: str) -> bool:
        """Verify an API key against the hash"""
        return self.key_hash == self.hash_key(key)

    def is_expired(self) -> bool:
        """Check if API key is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if API key is valid (active and not expired)"""
        return self.is_active and not self.is_expired() and not self.is_deleted

    def mark_used(self):
        """Update last_used_at timestamp"""
        self.last_used_at = datetime.utcnow()

    def revoke(self):
        """Revoke the API key"""
        self.is_active = False
