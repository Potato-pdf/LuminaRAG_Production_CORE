from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.schema import MetadataMode
from typing import List, Optional
from src.config import CHUNKING_CONFIG

def create_index_llamaindex(
    documents, 
    vector_store, 
    embed_model,
    chunk_size: int = CHUNKING_CONFIG["chunk_size"],              # Tamaño del chunk en tokens
    chunk_overlap: int = CHUNKING_CONFIG["chunk_overlap"],        # Solapamiento entre chunks
    chunk_window_size: int = CHUNKING_CONFIG["chunk_window_size"],# Número de oraciones por ventana
    include_metadata: bool = True        # Incluir metadatos (útil para DGA)
):
    # Crear un parseador de nodos personalizado para controlar el chunking
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=chunk_window_size,               # Ventana de oraciones
        window_metadata_key="window",                # Clave para metadatos de ventana
        original_text_metadata_key="original_text",  # Clave para texto original
        chunk_size=chunk_size,                       # Tamaño del chunk
        chunk_overlap=chunk_overlap                  # Solapamiento
    )
    print(f"Configuración de chunks: tamaño={chunk_size}, solapamiento={chunk_overlap}, ventana={chunk_window_size}")
    nodes = node_parser.get_nodes_from_documents(documents)
    print(f"Documentos divididos en {len(nodes)} chunks/nodos")
    if len(nodes) > 0:
        print(f"Ejemplo de chunk: {nodes[0].get_content(metadata_mode=MetadataMode.NONE)[:100]}...")
    index = VectorStoreIndex(
        nodes,
        vector_store=vector_store,
        embed_model=embed_model,
        show_progress=True  
    )
    
    return index
