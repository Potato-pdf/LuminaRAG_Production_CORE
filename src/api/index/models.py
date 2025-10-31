from pydantic import BaseModel, Field
from typing import Optional


class DocumentToIndex(BaseModel):
    """Payload model for indexing a document.

    Fields:
        empresa: Organization or company name the document belongs to.
        titulo: Title of the document.
        private: Whether the document is private (default: False).
    """

    empresa: str = Field(..., description="Organization or company name")
    titulo: str = Field(..., description="Document title")
    private: Optional[bool] = Field(False, description="Is the document private?")

    class Config:
        json_schema_extra = {
            "example": {
                "empresa": "FINFERSSA",
                "titulo": "Contrato de servicio",
                "private": False,
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

