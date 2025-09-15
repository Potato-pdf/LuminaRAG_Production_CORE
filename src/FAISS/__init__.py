"""
🌿 SISTEMA FAISS PARA RAG JERÁRQUICO
===================================

Sistema optimizado que reemplaza el meta-grafo con FAISS:
- Índice FAISS solo para raíces de documentos
- Búsqueda específica en árboles seleccionados
- Arquitectura limpia sin conexiones entre documentos
"""

from .root_finder import RootFinder
from .tree_graph import TreeGraphRAG
from .faiss_integration import (
    create_faiss_system_from_hierarchical,
    save_faiss_system,
    load_faiss_system,
    migrate_hierarchical_to_faiss,
    verify_faiss_system
)

__all__ = [
    'RootFinder',
    'TreeGraphRAG',
    'create_faiss_system_from_hierarchical',
    'save_faiss_system',
    'load_faiss_system',
    'migrate_hierarchical_to_faiss',
    'verify_faiss_system'
]