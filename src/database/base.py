"""
Base classes and mixins for database models.
Implements common patterns like timestamps and soft deletes.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps to models.
    Automatically managed by SQLAlchemy events.
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality.
    Records are marked as deleted instead of being removed from database.
    Useful for audit trails and data recovery.
    """
    deleted_at = Column(DateTime, nullable=True, default=None)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def soft_delete(self):
        """Mark record as deleted"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore soft-deleted record"""
        self.is_deleted = False
        self.deleted_at = None


class BaseModel(TimestampMixin, SoftDeleteMixin):
    """
    Base model with common fields for all database models.
    Includes:
    - Primary key (id)
    - Timestamps (created_at, updated_at)
    - Soft delete (deleted_at, is_deleted)
    """
    @declared_attr
    def __tablename__(cls):
        """Auto-generate table name from class name"""
        return cls.__name__.lower() + 's'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    def to_dict(self):
        """Convert model to dictionary (useful for serialization)"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
