"""
User model - Represents users within companies.
"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from src.database import Base
from src.database.base import BaseModel

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base, BaseModel):
    """
    User model.
    Users belong to a company and can have different roles.
    """
    __tablename__ = "users"

    # Basic Information
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    
    # Status and Permissions
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Company Relationship
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="users")
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    uploaded_documents = relationship("Document", back_populates="uploaded_by_user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', company_id={self.company_id})>"

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify a password against the hash"""
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        """Set user password (hashes automatically)"""
        self.hashed_password = self.hash_password(password)

    @property
    def is_admin(self) -> bool:
        """Check if user is admin (superuser)"""
        return self.is_superuser
