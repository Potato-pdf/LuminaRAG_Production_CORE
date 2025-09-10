import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de chunking
CHUNKING_CONFIG = {
    # Tamaño del chunk en tokens (determina cuánta información se incluye en cada fragmento)
    "chunk_size": int(os.getenv("CHUNK_SIZE")),
    
    # Solapamiento entre chunks en tokens (para mantener contexto entre fragmentos adyacentes)
    "chunk_overlap": int(os.getenv("CHUNK_OVERLAP")),
    
    # Número de oraciones por ventana para el SentenceWindowNodeParser
    "chunk_window_size": int(os.getenv("CHUNK_WINDOW_SIZE")),
}

# Configuración de embedding
EMBEDDING_CONFIG = {
    # Dimensión del vector de embedding
    "embedding_dim": int(os.getenv("EMBEDDING_DIM")),
    # Modelo de embedding multilingüe a utilizar
    "model_name": os.getenv("EMBEDDING_MODEL"),
}

# Configuración de parsing de documentos
PARSING_CONFIG = {
    "result_type": "markdown",  # "text", "markdown", "json", "structured"
    "language": "es",           # Idioma para LlamaParse
    "verbose": True,            # Mostrar información del proceso
    "supported_extensions": [".pdf", ".docx"],  # Extensiones soportadas
}

# ============================================================================
# CONFIGURACIÓN SENSIBLE - DESDE .ENV
# ============================================================================

# API Keys (sensibles)
API_CONFIG = {
    "llama_cloud_api_key": os.getenv("LLAMA_CLOUD_API_KEY"),
}

# Configuración de Milvus (usando variables sensibles)
MILVUS_CONFIG = {
    "host": os.getenv("MILVUS_HOST"),
    "port": os.getenv("MILVUS_PORT"),
    "user": os.getenv("MILVUS_USER"),
    "password": os.getenv("MILVUS_PASSWORD"),
}

# Configuración de Ollama
OLLAMA_CONFIG = {
    "model": os.getenv("OLLAMA_MODEL"),
    "base_url": os.getenv("OLLAMA_BASE_URL"),
}

# Configuración de rutas
PATH_CONFIG = {
    "pdf_directory": os.getenv("PDF_DIRECTORY"),
    "doc_directory": os.getenv("PDF_DIRECTORY"),  # Centralizado en pdfs
}

# ============================================================================
# CONFIGURACIÓN DE ALMACENAMIENTO
# ============================================================================

STORAGE_CONFIG = {
    "base_dir": "storage",
    "graphs_dir": "storage/graphs",
    "cache_dir": "storage/cache",
    "logs_dir": "storage/logs",
    "graph_filename": "document_graph.pkl",
    "graph_path": "storage/graphs/document_graph.pkl"
}

# Configuración de fuentes de documentos (para arquitectura modular)
DOCUMENT_SOURCE_CONFIG = {
    "type": "local",  # "local", "api", "database", etc.
    "parser": "llama_parse"  # "llama_parse", "simple", etc.
}