"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import re

from src.database import get_db
from src.database.models.user import User
from src.database.repositories.user import UserRepository
from src.database.repositories.company import CompanyRepository
from src.database.repositories.api_key import APIKeyRepository
from src.auth import (
    create_tokens_for_user,
    get_current_active_user,
    decode_token
)
from src.api.schemas.auth import (
    Token,
    UserLogin,
    UserRegister,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyInfo
)
from src.api.schemas.user import UserResponse

router = APIRouter()


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user and create their company.
    
    - Creates a new company for the user
    - Creates the user as the first user of that company
    - Returns JWT tokens for immediate login
    """
    user_repo = UserRepository(db)
    company_repo = CompanyRepository(db)
    
    # Check if email already exists
    existing_user = user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create company slug from name
    company_slug = slugify(user_data.company_name)
    
    # Check if company slug already exists
    existing_company = company_repo.get_by_slug(company_slug)
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with slug '{company_slug}' already exists"
        )
    
    # Create company
    company = company_repo.create_company(
        name=user_data.company_name,
        slug=company_slug
    )
    
    # Create user
    user = user_repo.create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        company_id=company.id,
        is_superuser=False  # First user is not superuser by default
    )
    
    # Create tokens
    tokens = create_tokens_for_user(user.id, user.email, user.company_id)
    
    return tokens


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    
    - Authenticates user credentials
    - Returns JWT tokens
    """
    user_repo = UserRepository(db)
    
    # Authenticate user
    user = user_repo.authenticate(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    tokens = create_tokens_for_user(user.id, user.email, user.company_id)
    
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - Validates refresh token
    - Returns new access and refresh tokens
    """
    # Decode refresh token
    payload = decode_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user_id = int(payload.get("sub"))
    user_repo = UserRepository(db)
    user = user_repo.get(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new tokens
    tokens = create_tokens_for_user(user.id, user.email, user.company_id)
    
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    - Requires valid JWT token
    - Returns user profile
    """
    return current_user


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key for the current user.
    
    - Requires authentication
    - Returns the API key (only shown once!)
    """
    api_key_repo = APIKeyRepository(db)
    
    # Create API key
    api_key, plain_key = api_key_repo.create_api_key(
        name=key_data.name,
        company_id=current_user.company_id,
        user_id=current_user.id,
        expires_in_days=key_data.expires_in_days
    )
    
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        api_key=plain_key,  # Only time the key is shown!
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None
    )


@router.get("/api-keys", response_model=list[APIKeyInfo])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for the current user.
    
    - Requires authentication
    - Does not show the actual keys (only metadata)
    """
    api_key_repo = APIKeyRepository(db)
    
    # Get user's API keys
    api_keys = api_key_repo.get_by_user(current_user.id)
    
    return [
        APIKeyInfo(
            id=key.id,
            name=key.name,
            is_active=key.is_active,
            expires_at=key.expires_at.isoformat() if key.expires_at else None,
            last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
            created_at=key.created_at.isoformat()
        )
        for key in api_keys
    ]


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Revoke an API key.
    
    - Requires authentication
    - Can only revoke own API keys
    """
    api_key_repo = APIKeyRepository(db)
    
    # Get API key
    api_key = api_key_repo.get(key_id)
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check ownership
    if api_key.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Revoke key
    api_key_repo.revoke(key_id)
    
    return None
