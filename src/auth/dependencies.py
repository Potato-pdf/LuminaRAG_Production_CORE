"""
FastAPI dependencies for authentication and authorization.
Implements Dependency Injection pattern.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models.user import User
from src.database.models.company import Company
from src.database.repositories.user import UserRepository
from src.database.repositories.api_key import APIKeyRepository
from src.auth.jwt import decode_token

# HTTP Bearer scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_repo = UserRepository(db)
    user = user_repo.get(int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (must be active).
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current superuser (must be superuser).
    
    Args:
        current_user: Current active user
        
    Returns:
        Current superuser
        
    Raises:
        HTTPException: If user is not superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user


async def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> tuple[User, Company]:
    """
    Verify API key and return associated user and company.
    
    Args:
        x_api_key: API key from header
        db: Database session
        
    Returns:
        Tuple of (User, Company)
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # Verify API key
    api_key_repo = APIKeyRepository(db)
    api_key = api_key_repo.verify_and_update(x_api_key)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Get user and company
    user_repo = UserRepository(db)
    user = user_repo.get(api_key.user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return user, user.company


async def get_user_or_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get user from either JWT token or API key.
    Tries JWT first, then API key.
    
    Args:
        credentials: HTTP Bearer credentials (optional)
        x_api_key: API key from header (optional)
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If neither authentication method is valid
    """
    # Try JWT first
    if credentials:
        try:
            return await get_current_user(credentials, db)
        except HTTPException:
            pass
    
    # Try API key
    if x_api_key:
        user, _ = await verify_api_key(x_api_key, db)
        return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required (JWT or API key)"
    )


def check_company_access(user: User, company_slug: str) -> bool:
    """
    Check if user has access to a company.
    
    Args:
        user: Current user
        company_slug: Company slug to check
        
    Returns:
        True if user has access, False otherwise
    """
    # Superusers have access to all companies
    if user.is_superuser:
        return True
    
    # Regular users only have access to their own company
    return user.company.slug == company_slug
