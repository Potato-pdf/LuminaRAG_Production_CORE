# src/parse_docs/parse_docs.py
from typing import List, Optional
from llama_index.core import Document
from src.config import DOCUMENT_SOURCE_CONFIG

def parse_documents(directory_path: str = None, api_key: Optional[str] = None) -> List[Document]:

    # 1. Obtener source configurada
    if DOCUMENT_SOURCE_CONFIG["type"] == "local":
        from .sources.local_source import LocalFileSource
        source = LocalFileSource()  # Sin parámetros - usa configuración
    # elif DOCUMENT_SOURCE_CONFIG["type"] == "api":
        #from .sources.api_source import APISource  # ← FUTURO
        #source = APISource()

    # 2. Obtener parser configurada
    if DOCUMENT_SOURCE_CONFIG["parser"] == "llama_parse":
        from .parsers.llama_parse import LlamaParseParser
        parser = LlamaParseParser(api_key)
    
    # 3. Ejecutar proceso (NO CAMBIA)
    file_paths = source.get_file_paths()
    if not file_paths:
        print(f"No se encontraron archivos")
        return []
    
    print(f"📄 Procesando {len(file_paths)} archivos...")
    documents = parser.parse_files(file_paths)
    print(f"✅ Se generaron {len(documents)} documentos.")
    
    return documents