"""
📋 MODELOS DE DATOS PARA LA API
================================

Modelos Pydantic para request/response de la API REST.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class QueryRequest(BaseModel):
    """Modelo para solicitud de consulta"""
    query: str = Field(..., min_length=1, max_length=2000, description="Consulta del usuario")
    k: int = Field(5, ge=1, le=20, description="Número de chunks a retornar")
    k_roots: int = Field(5, ge=1, le=10, description="Número de raíces a considerar")
    include_context: bool = Field(True, description="Incluir contexto adicional en la respuesta")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "¿Cuáles son los procedimientos principales del documento?",
                "k": 5,
                "k_roots": 5,
                "include_context": True
            }
        }


class ChunkInfo(BaseModel):
    """Información de un chunk relevante"""
    chunk_id: str
    content: str
    score: float
    document: str
    metadata: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Modelo para respuesta de consulta"""
    query: str
    answer: str
    chunks: List[ChunkInfo]
    documents_used: List[str]
    processing_time: float
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "¿Cuáles son los procedimientos principales?",
                "answer": "Los procedimientos principales son...",
                "chunks": [
                    {
                        "chunk_id": "chunk_123",
                        "content": "Contenido del fragmento...",
                        "score": 0.95,
                        "document": "manual_tecnico.pdf"
                    }
                ],
                "documents_used": ["manual_tecnico.pdf"],
                "processing_time": 1.23,
                "timestamp": "2025-10-13T10:30:00"
            }
        }


class SystemStats(BaseModel):
    """Estadísticas del sistema"""
    total_documents: int
    total_chunks: int
    indexed_roots: int
    system_status: str
    faiss_index_size: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_documents": 10,
                "total_chunks": 250,
                "indexed_roots": 10,
                "system_status": "operational",
                "faiss_index_size": 10
            }
        }


class DocumentInfo(BaseModel):
    """Información de un documento"""
    document_id: str
    root_chunk_id: str
    total_chunks: int
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "manual_tecnico.pdf",
                "root_chunk_id": "chunk_root_001",
                "total_chunks": 25
            }
        }


class HealthResponse(BaseModel):
    """Respuesta del health check"""
    status: str
    faiss_loaded: bool
    llm_connected: bool
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "faiss_loaded": True,
                "llm_connected": True,
                "details": {
                    "documents": 10,
                    "indexed_roots": 10
                }
            }
        }


class ErrorResponse(BaseModel):
    """Respuesta de error"""
    error: str
    detail: Optional[str] = None
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Query processing failed",
                "detail": "LLM connection timeout",
                "timestamp": "2025-10-13T10:30:00"
            }
        }
