"""
Base repository with generic CRUD operations.
Implements Repository Pattern for data access abstraction.
"""
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations.
    All specific repositories should inherit from this class.
    """

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository with model class and database session.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    def get(self, id: int, include_deleted: bool = False) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            id: Record ID
            include_deleted: Whether to include soft-deleted records
            
        Returns:
            Model instance or None if not found
        """
        query = self.db.query(self.model).filter(self.model.id == id)
        
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        
        return query.first()

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filters.
        
        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            filters: Dictionary of field:value filters
            include_deleted: Whether to include soft-deleted records
            
        Returns:
            List of model instances
        """
        query = self.db.query(self.model)
        
        # Apply soft delete filter
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        
        # Apply custom filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()

    def count(self, filters: Optional[Dict[str, Any]] = None, include_deleted: bool = False) -> int:
        """
        Count records matching filters.
        
        Args:
            filters: Dictionary of field:value filters
            include_deleted: Whether to include soft-deleted records
            
        Returns:
            Number of matching records
        """
        query = self.db.query(self.model)
        
        if not include_deleted:
            query = query.filter(self.model.is_deleted == False)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.count()

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create a new record.
        
        Args:
            obj_in: Dictionary with field values
            
        Returns:
            Created model instance
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """
        Update an existing record.
        
        Args:
            db_obj: Existing model instance
            obj_in: Dictionary with updated field values
            
        Returns:
            Updated model instance
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int, soft: bool = True) -> bool:
        """
        Delete a record (soft delete by default).
        
        Args:
            id: Record ID
            soft: If True, perform soft delete; if False, hard delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        db_obj = self.get(id, include_deleted=True)
        
        if not db_obj:
            return False
        
        if soft:
            db_obj.soft_delete()
            self.db.commit()
        else:
            self.db.delete(db_obj)
            self.db.commit()
        
        return True

    def restore(self, id: int) -> Optional[ModelType]:
        """
        Restore a soft-deleted record.
        
        Args:
            id: Record ID
            
        Returns:
            Restored model instance or None if not found
        """
        db_obj = self.get(id, include_deleted=True)
        
        if not db_obj or not db_obj.is_deleted:
            return None
        
        db_obj.restore()
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
