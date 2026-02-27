from pydantic import BaseModel, Field
from typing import Optional


class DocumentToIndex(BaseModel):
    """Payload model for indexing a document.

    Fields:
        empresa: Organization or company name the document belongs to.
        private: Whether the document is private (default: False).
        force_reindex: Force re-indexing even if collection already exists (default: False).
    """

    empresa: str = Field(..., description="Organization or company name")
    private: Optional[bool] = Field(False, description="Is the document private?")
    force_reindex: Optional[bool] = Field(False, description="Force re-indexing if collection exists")

    class Config:
        json_schema_extra = {
            "example": {
                "empresa": "FINFERSSA",
                "private": False,
                "force_reindex": False
            }
        }


class IndexResponse(BaseModel):
    """Response model for indexing operations."""

    success: bool = Field(..., description="Whether the indexing was successful")
    message: str = Field(..., description="Response message")
    documents_processed: int = Field(0, description="Number of documents processed")
    chunks_created: int = Field(0, description="Number of chunks created")
    milvus_collection: str = Field(..., description="Milvus collection name")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Documentos indexados exitosamente",
                "documents_processed": 5,
                "chunks_created": 150,
                "milvus_collection": "lumina_hierarchical"
            }
        }

