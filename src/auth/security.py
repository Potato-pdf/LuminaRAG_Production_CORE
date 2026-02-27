"""
Security utilities for password hashing and API key generation.
"""
import secrets
import hashlib
from passlib.context import CryptContext

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_api_key() -> str:
    """
    Generate a secure random API key.
    Format: lum_<32_random_characters>
    
    Returns:
        Generated API key
    """
    random_part = secrets.token_urlsafe(32)
    return f"lum_{random_part}"


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.
    Uses SHA-256 for fast verification.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        Hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hash.
    
    Args:
        plain_key: Plain text API key
        hashed_key: Hashed API key to compare against
        
    Returns:
        True if key matches, False otherwise
    """
    return hash_api_key(plain_key) == hashed_key
