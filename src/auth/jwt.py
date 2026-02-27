"""
JWT token management using Factory Pattern.
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt

# JWT Configuration from environment
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class TokenFactory:
    """
    Factory class for creating different types of JWT tokens.
    Implements Factory Pattern for token creation.
    """

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create an access token (short-lived).
        
        Args:
            data: Data to encode in the token
            expires_delta: Custom expiration time (optional)
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create a refresh token (long-lived).
        
        Args:
            data: Data to encode in the token
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Convenience function to create access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Custom expiration time (optional)
        
    Returns:
        Encoded JWT token
    """
    return TokenFactory.create_access_token(data, expires_delta)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Convenience function to create refresh token.
    
    Args:
        data: Data to encode in the token
        
    Returns:
        Encoded JWT token
    """
    return TokenFactory.create_refresh_token(data)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to decode token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token data or None if invalid
    """
    return TokenFactory.decode_token(token)


def create_tokens_for_user(user_id: int, email: str, company_id: int) -> Dict[str, str]:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        user_id: User ID
        email: User email
        company_id: Company ID
        
    Returns:
        Dictionary with access_token and refresh_token
    """
    token_data = {
        "sub": str(user_id),
        "email": email,
        "company_id": company_id
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
