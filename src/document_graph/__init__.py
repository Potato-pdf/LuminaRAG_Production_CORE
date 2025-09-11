try:
    from .simple_graph import SimpleDocumentGraph, create_simple_rag_graph
    from .hierarchical_graph import HierarchicalDocumentGraph, create_hierarchical_rag_graph
    
    __all__ = [
        'SimpleDocumentGraph',           # Interface original del grafo
        'create_simple_rag_graph',       # Función para crear grafo simple (LEGACY)
        'HierarchicalDocumentGraph',     # Nueva interface jerárquica
        'create_hierarchical_rag_graph', # Función para crear grafo jerárquico (NUEVO)
    ]
    
    # Aliases para compatibilidad
    DocumentGraph = SimpleDocumentGraph
    
    def create_graph_from_chunks(chunks_data):
        """Alias para compatibilidad - usa arquitectura jerárquica por defecto"""
        return create_hierarchical_rag_graph(chunks_data)
    
except ImportError as e:
    print(f"❌ Error importing graph components: {e}")
    
    __all__ = []
    
    class SimpleDocumentGraph:
        def __init__(self):
            raise ImportError("NetworkX not available. Install with: pip install networkx")
    
    class HierarchicalDocumentGraph:
        def __init__(self):
            raise ImportError("NetworkX not available. Install with: pip install networkx")
    
    def create_simple_rag_graph(chunks_data):
        raise ImportError("NetworkX not available. Install with: pip install networkx")
    
    def create_hierarchical_rag_graph(chunks_data):
        raise ImportError("NetworkX not available. Install with: pip install networkx")
