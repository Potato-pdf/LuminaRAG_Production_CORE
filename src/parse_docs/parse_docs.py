# src/parse_docs/parse_docs.py
from typing import List, Optional, Tuple
from llama_index.core import Document
from src.config import DOCUMENT_SOURCE_CONFIG


def parse_documents(directory_path: str = None, api_key: Optional[str] = None) -> List[Document]:
    """Parse documents from configured source (legacy function)"""
    documents, _ = parse_documents_with_metadata(directory_path, api_key)
    return documents


def parse_documents_with_metadata(directory_path: str = None, api_key: Optional[str] = None) -> Tuple[List[Document], List[dict]]:
    """Parse documents from configured source with metadata"""

    # 1. Obtener source configurada
    if DOCUMENT_SOURCE_CONFIG["type"] == "local":
        from .sources.local_source import LocalFileSource
        source = LocalFileSource()  # Sin parámetros - usa configuración
        documents_metadata = []  # Local source no tiene metadata especial
    elif DOCUMENT_SOURCE_CONFIG["type"] == "api":
        from .sources.api_source import APISource
        source = APISource()
        # API source devuelve metadata de empresa/privacidad
        documents_metadata = source.get_documents_with_metadata()

    # 2. Obtener parser configurada
    if DOCUMENT_SOURCE_CONFIG["parser"] == "llama_parse":
        from .parsers.llama_parse import LlamaParseParser
        parser = LlamaParseParser(api_key)

    # 3. Ejecutar proceso
    if DOCUMENT_SOURCE_CONFIG["type"] == "api" and documents_metadata:
        # Para API source, usar los documentos con metadata
        file_paths = [doc.local_path for doc in documents_metadata]
        documents = parser.parse_files(file_paths)

        # Agregar metadata a los documentos
        for i, doc in enumerate(documents):
            if i < len(documents_metadata):
                metadata = documents_metadata[i]
                doc.metadata.update({
                    'empresa': metadata.empresa,
                    'private': metadata.private,
                    's3_key': metadata.s3_key,
                    'file_name': metadata.file_name
                })

        # Marcar archivos como procesados
        source.mark_files_processed(file_paths)

    else:
        # Para local source o si no hay metadata
        file_paths = source.get_file_paths()
        if not file_paths:
            print("No se encontraron archivos")
            return [], []

        print(f"📄 Procesando {len(file_paths)} archivos...")
        documents = parser.parse_files(file_paths)

        # Marcar archivos como procesados (solo para API source)
        if hasattr(source, 'mark_files_processed'):
            source.mark_files_processed(file_paths)

    print(f"✅ Se generaron {len(documents)} documentos.")
    return documents, documents_metadata