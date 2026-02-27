"""
Document management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import boto3
from pathlib import Path

from src.database import get_db
from src.database.models.user import User
from src.database.repositories.document import DocumentRepository
from src.auth import get_current_active_user, document_access, document_edit
from src.api.schemas.document import DocumentResponse, DocumentList, DocumentUpdate
from src.config import S3_CONFIG

router = APIRouter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".doc", ".md"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    name = Path(filename).stem
    ext = Path(filename).suffix
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    return f"{name}{ext}".lower()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    is_private: bool = Form(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document.
    
    - Validates file type and size
    - Uploads to S3
    - Creates database record
    - Triggers indexing
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Sanitize filename
    sanitized_name = sanitize_filename(file.filename)
    
    # Create S3 key
    privacy_str = "private" if is_private else "public"
    s3_key = f"{current_user.company.slug}/{privacy_str}/{sanitized_name}"
    
    # Upload to S3
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=S3_CONFIG["access_key"],
            aws_secret_access_key=S3_CONFIG["secret_key"],
            region_name=S3_CONFIG["region"]
        )
        
        s3_client.put_object(
            Bucket=S3_CONFIG["bucket_name"],
            Key=s3_key,
            Body=content
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload to S3: {str(e)}"
        )
    
    # Create document record
    doc_repo = DocumentRepository(db)
    document = doc_repo.create_document(
        filename=sanitized_name,
        original_filename=file.filename,
        s3_key=s3_key,
        file_type=file_ext[1:],  # Remove dot
        file_size=file_size,
        is_private=is_private,
        company_id=current_user.company_id,
        uploaded_by=current_user.id
    )
    
    # TODO: Trigger async indexing task
    
    return document


@router.get("", response_model=DocumentList)
async def list_documents(
    is_private: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List documents for the current user's company.
    
    - Optionally filter by privacy
    - Supports pagination
    """
    doc_repo = DocumentRepository(db)
    
    documents = doc_repo.get_by_company(
        company_id=current_user.company_id,
        is_private=is_private,
        skip=skip,
        limit=limit
    )
    
    total = doc_repo.count(
        filters={"company_id": current_user.company_id},
        include_deleted=False
    )
    
    return DocumentList(
        total=total,
        documents=documents,
        skip=skip,
        limit=limit
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    doc_repo = DocumentRepository(db)
    document = doc_repo.get(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check access
    document_access.check_or_raise(current_user, document)
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document.
    
    - Removes from S3
    - Soft deletes from database
    - Triggers re-indexing
    """
    doc_repo = DocumentRepository(db)
    document = doc_repo.get(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check edit permission
    document_edit.check_or_raise(current_user, document)
    
    # Delete from S3
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=S3_CONFIG["access_key"],
            aws_secret_access_key=S3_CONFIG["secret_key"],
            region_name=S3_CONFIG["region"]
        )
        
        s3_client.delete_object(
            Bucket=S3_CONFIG["bucket_name"],
            Key=document.s3_key
        )
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Failed to delete from S3: {e}")
    
    # Soft delete from database
    doc_repo.delete(document_id, soft=True)
    
    # TODO: Trigger re-indexing of collection
    
    return None


@router.patch("/{document_id}/privacy", response_model=DocumentResponse)
async def update_document_privacy(
    document_id: int,
    is_private: bool,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update document privacy setting.
    
    - Moves document in S3 if needed
    - Updates database
    - Triggers re-indexing
    """
    doc_repo = DocumentRepository(db)
    document = doc_repo.get(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check edit permission
    document_edit.check_or_raise(current_user, document)
    
    # Update privacy
    updated_doc = doc_repo.update_privacy(document_id, is_private)
    
    # TODO: Move file in S3 and trigger re-indexing
    
    return updated_doc
