"""
Company Configuration model - Stores per-company settings.
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.database import Base
from src.database.base import BaseModel


class CompanyConfig(Base, BaseModel):
    """
    Company Configuration model.
    Stores customizable settings per company.
    """
    __tablename__ = "company_configs"

    # Company Relationship (One-to-One)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=False, index=True)
    company = relationship("Company", back_populates="config")
    
    # Embedding Configuration
    embedding_model = Column(String(255), default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    embedding_dim = Column(Integer, default=384)
    
    # Chunking Configuration
    chunk_size = Column(Integer, default=512)
    chunk_overlap = Column(Integer, default=50)
    chunk_window_size = Column(Integer, default=3)
    
    # LLM Configuration
    llm_model = Column(String(255), default="llama3.2")
    llm_temperature = Column(Float, default=0.1)
    llm_max_tokens = Column(Integer, default=512)
    
    # Custom Settings (JSONB for flexibility)
    custom_settings = Column(JSON, nullable=True, default={})

    def __repr__(self):
        return f"<CompanyConfig(id={self.id}, company_id={self.company_id})>"

    def get_setting(self, key: str, default=None):
        """Get a custom setting by key"""
        if self.custom_settings is None:
            return default
        return self.custom_settings.get(key, default)

    def set_setting(self, key: str, value):
        """Set a custom setting"""
        if self.custom_settings is None:
            self.custom_settings = {}
        self.custom_settings[key] = value

    def to_config_dict(self) -> dict:
        """Convert to configuration dictionary"""
        return {
            "embedding": {
                "model_name": self.embedding_model,
                "dimension": self.embedding_dim
            },
            "chunking": {
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "chunk_window_size": self.chunk_window_size
            },
            "llm": {
                "model_name": self.llm_model,
                "temperature": self.llm_temperature,
                "max_tokens": self.llm_max_tokens
            },
            "custom": self.custom_settings or {}
        }
