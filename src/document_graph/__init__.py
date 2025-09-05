"""
Document Graph Module - Módulo de Grafo de Documentos
====================================================

Este módulo proporciona capacidades de grafo para organizar y conectar 
fragmentos de documentos, facilitando navegación y análisis contextual.

Arquitectura Modular:
- SimpleDocumentGraph: Interface principal (Facade)
- GraphManager: Operaciones CRUD básicas
- GraphAnalyzer: Análisis y consultas avanzadas
- GraphExporter: Exportación y persistencia  
- GraphBuilder: Construcción de grafos

Funcionalidades principales:
- Crear grafos de documentos a partir de chunks
- Conectar documentos relacionados
- Análisis de relaciones y rutas entre documentos
- Búsqueda contextual basada en grafos
- Exportación en múltiples formatos

Usage:
    from src.document_graph import SimpleDocumentGraph, create_simple_rag_graph
    
    # Crear grafo desde chunks
    graph = create_simple_rag_graph(chunks_data)
    
    # Usar directamente
    graph = SimpleDocumentGraph()
    graph.add_chunk('id', 'content', metadata)
"""

# Interface principal
try:
    from .simple_graph import SimpleDocumentGraph, create_simple_rag_graph

    # Módulos especializados (opcional para uso avanzado)
    from .core.graph_manager import GraphManager
    from .core.graph_analyzer import GraphAnalyzer
    from .core.graph_exporter import GraphExporter
    from .utils.graph_builder import GraphBuilder

    # Lista de exportaciones públicas
    __all__ = [
        # Interface principal (recomendado para la mayoría de casos)
        'SimpleDocumentGraph',
        'create_simple_rag_graph',
        
        # Módulos especializados (para uso avanzado)
        'GraphManager',
        'GraphAnalyzer', 
        'GraphExporter',
        'GraphBuilder'
    ]
    
    # Alias para compatibilidad
    DocumentGraph = SimpleDocumentGraph
    
    def create_graph_from_chunks(chunks_data):
        """Alias para compatibilidad"""
        return create_simple_rag_graph(chunks_data)
    
    # Información del módulo
    __version__ = "2.1.0"
    __author__ = "GitHub Copilot"
    __description__ = "Simple and clean document graph system for RAG applications"
    
except ImportError as e:
    print(f"❌ Error importing graph components: {e}")
    print("Make sure NetworkX is installed: pip install networkx")
    
    # Fallback
    __all__ = []
    
    class SimpleDocumentGraph:
        def __init__(self):
            raise ImportError("NetworkX not available. Install with: pip install networkx")
    
    def create_simple_rag_graph(chunks_data):
        raise ImportError("NetworkX not available. Install with: pip install networkx")
