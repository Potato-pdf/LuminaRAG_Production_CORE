"""
⚙️ CONFIGURACIONES DEL SISTEMA LUMINA RAG
=========================================

Configuraciones centralizadas para todos los componentes del sistema.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# =============================================================================
# CONFIGURACIÓN DE CHUNKING
# =============================================================================
CHUNKING_CONFIG = {
    "chunk_size": int(os.getenv("CHUNK_SIZE", "512")),
    "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "50")),
    "chunk_window_size": int(os.getenv("CHUNK_WINDOW_SIZE", "3")),
}

# =============================================================================
# CONFIGURACIÓN DE EMBEDDINGS
# =============================================================================
EMBEDDING_CONFIG = {
    "model_name": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
    "dimension": int(os.getenv("EMBEDDING_DIM", "384")),
    "device": "cpu",  # Para Docker, usar CPU
}

# =============================================================================
# CONFIGURACIÓN DE LLM
# =============================================================================
LLM_CONFIG = {
    "model_name": os.getenv("OLLAMA_MODEL", "llama3.2"),
    "api_key": os.getenv("LLAMA_CLOUD_API_KEY", ""),
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.1")),
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "512")),
}

# =============================================================================
# CONFIGURACIÓN DE API
# =============================================================================
API_CONFIG = {
    "llama_cloud_api_key": os.getenv("LLAMA_CLOUD_API_KEY", ""),
    "host": "0.0.0.0",
    "port": 8000,
}

# =============================================================================
# CONFIGURACIÓN DE STORAGE
# =============================================================================
STORAGE_CONFIG = {
    "base_dir": os.getenv("STORAGE_BASE_DIR", "/app/storage"),
    "graphs_dir": os.getenv("GRAPHS_DIR", "/app/storage/graphs"),
    "faiss_dir": os.getenv("FAISS_DIR", "/app/storage/faiss_collections"),
    "graph_path": os.getenv("GRAPH_PATH", "/app/storage/graphs/hierarchical_graph.pkl"),
}

# =============================================================================
# CONFIGURACIÓN DE MILVUS (si se usa)
# =============================================================================
MILVUS_CONFIG = {
    "host": os.getenv("MILVUS_HOST", "localhost"),
    "port": os.getenv("MILVUS_PORT", "19530"),
    "user": os.getenv("MILVUS_USER", ""),
    "password": os.getenv("MILVUS_PASSWORD", ""),
    "collection_name": os.getenv("MILVUS_COLLECTION", "lumina_hierarchical"),
}

# =============================================================================
# CONFIGURACIÓN DE FUENTE DE DOCUMENTOS
# =============================================================================
DOCUMENT_SOURCE_CONFIG = {
    "type": os.getenv("DOCUMENT_SOURCE_TYPE", "api"),  # "local" o "api"
    "parser": os.getenv("DOCUMENT_PARSER", "llama_parse"),  # "llama_parse" o "simple"
    "local_directory": os.getenv("LOCAL_DOC_DIR", "/app/pdfs"),
    "s3_bucket": os.getenv("S3_BUCKET", "lumina-documents"),
    "s3_prefix": os.getenv("S3_PREFIX", ""),  # Prefijo opcional en S3
}

# =============================================================================
# CONFIGURACIÓN DE S3 (si se usa)
# =============================================================================
S3_CONFIG = {
    "bucket_name": os.getenv("S3_BUCKET", "lumina-documents"),
    "region": os.getenv("S3_REGION", "us-east-1"),
    "access_key": os.getenv("AWS_ACCESS_KEY_ID", ""),
    "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
}

# =============================================================================
# CONFIGURACIÓN DE S3 PARA ÍNDICES FAISS
# =============================================================================
S3_FAISS_CONFIG = {
    "bucket_name": os.getenv("S3_FAISS_BUCKET", os.getenv("S3_BUCKET", "lumina-documents")),
    "region": os.getenv("S3_FAISS_REGION", os.getenv("S3_REGION", "us-east-1")),
    "access_key": os.getenv("AWS_ACCESS_KEY_ID", ""),
    "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
    "prefix": os.getenv("S3_FAISS_PREFIX", "faiss_indices/"),
}