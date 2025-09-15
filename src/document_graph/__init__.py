try:
    from .hierarchical_graph import HierarchicalDocumentGraph, create_hierarchical_rag_graph
    
    __all__ = [
        'HierarchicalDocumentGraph',     # Interface jerárquica principal
        'create_hierarchical_rag_graph', # Función para crear grafo jerárquico
    ]
    
    # Alias para compatibilidad
    DocumentGraph = HierarchicalDocumentGraph
    
    def create_graph_from_chunks(chunks_data):
        """Crear grafo jerárquico desde chunks"""
        return create_hierarchical_rag_graph(chunks_data)
    
except ImportError as e:
    print(f"❌ Error importing graph components: {e}")
    
    __all__ = []
    
    class HierarchicalDocumentGraph:
        def __init__(self):
            raise ImportError("NetworkX not available. Install with: pip install networkx")
    
    def create_hierarchical_rag_graph(chunks_data):
        raise ImportError("NetworkX not available. Install with: pip install networkx")
