"""
Admin API endpoints for company management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.database.models.user import User
from src.database.repositories.company import CompanyRepository
from src.database.repositories.user import UserRepository
from src.auth import get_current_superuser
from src.api.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyWithStats
)
from src.api.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Create a new company (admin only).
    """
    company_repo = CompanyRepository(db)
    
    # Check if slug already exists
    existing = company_repo.get_by_slug(company_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with slug '{company_data.slug}' already exists"
        )
    
    company = company_repo.create_company(
        name=company_data.name,
        slug=company_data.slug,
        max_documents=company_data.max_documents,
        max_storage_gb=company_data.max_storage_gb,
        max_queries_per_month=company_data.max_queries_per_month
    )
    
    return company


@router.get("/companies", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    List all companies (admin only).
    """
    company_repo = CompanyRepository(db)
    companies = company_repo.get_multi(skip=skip, limit=limit)
    return companies


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Get company details (admin only).
    """
    company_repo = CompanyRepository(db)
    company = company_repo.get(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.get("/companies/{company_id}/stats", response_model=CompanyWithStats)
async def get_company_stats(
    company_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Get company with usage statistics (admin only).
    """
    company_repo = CompanyRepository(db)
    company_with_stats = company_repo.get_with_stats(company_id)
    
    if not company_with_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return CompanyWithStats(
        **company_with_stats["company"].__dict__,
        stats=company_with_stats["stats"]
    )


@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Update company (admin only).
    """
    company_repo = CompanyRepository(db)
    company = company_repo.get(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update only provided fields
    update_data = company_data.dict(exclude_unset=True)
    updated_company = company_repo.update(company, update_data)
    
    return updated_company


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Delete company (admin only).
    """
    company_repo = CompanyRepository(db)
    success = company_repo.delete(company_id, soft=True)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return None


@router.post("/companies/{company_id}/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_in_company(
    company_id: int,
    user_data: UserCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    Create a user in a specific company (admin only).
    """
    company_repo = CompanyRepository(db)
    user_repo = UserRepository(db)
    
    # Verify company exists
    company = company_repo.get(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if email already exists
    existing_user = user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = user_repo.create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        company_id=company_id,
        is_superuser=user_data.is_superuser
    )
    
    return user


@router.get("/companies/{company_id}/users", response_model=List[UserResponse])
async def list_company_users(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    List users in a company (admin only).
    """
    user_repo = UserRepository(db)
    users = user_repo.get_by_company(company_id, skip=skip, limit=limit)
    return users
