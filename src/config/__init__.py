"""
Módulo de inicialización para el paquete de configuración.
Permite importar configuraciones directamente desde src.config
"""

from .settings import (
    CHUNKING_CONFIG,
    EMBEDDING_CONFIG,
    PARSING_CONFIG,
    MILVUS_CONFIG,
    OLLAMA_CONFIG,
    PATH_CONFIG,
    STORAGE_CONFIG,
    API_CONFIG,
    DOCUMENT_SOURCE_CONFIG,
    S3_CONFIG
)

__all__ = [
    'CHUNKING_CONFIG',
    'EMBEDDING_CONFIG', 
    'PARSING_CONFIG',
    'MILVUS_CONFIG',
    'OLLAMA_CONFIG',
    'PATH_CONFIG',
    'STORAGE_CONFIG',
    'API_CONFIG',
    'DOCUMENT_SOURCE_CONFIG',
    'S3_CONFIG'
]
