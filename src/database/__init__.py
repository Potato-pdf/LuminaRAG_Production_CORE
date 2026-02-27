"""
Database configuration and session management.
Implements Singleton pattern for database session.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Generator

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lumina_user:lumina_pass@localhost:5432/lumina_rag")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints to get database session.
    Implements context manager pattern for automatic cleanup.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session outside of FastAPI.
    
    Usage:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    Should be called on application startup.
    """
    from src.database.models import user, company, api_key, document, company_config
    Base.metadata.create_all(bind=engine)


__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_context",
    "init_db"
]
