"""
Document Graph Augmentation (DGA) - Sistema modular de grafos dirigidos para RAG
Sistema completo para mejorar la recuperación contextual mediante grafos de documentos.
"""

# Importaciones principales
from .graph_core import DocumentGraphCore, Edge, Vertex
from .graph_algorithms import GraphAnalyzer
from .document_reconstructor import DocumentReconstructor
from .rag_integration import RAGDocumentGraphIntegration

# Clase principal que unifica todas las funcionalidades
class DocumentGraphAugmentation(DocumentGraphCore):
    """
    Clase principal que combina todas las funcionalidades del sistema DGA
    Hereda de DocumentGraphCore y agrega funcionalidades avanzadas
    """
    
    def __init__(self, directed: bool = True):
        super().__init__(directed)
        self.analyzer = GraphAnalyzer(self)
        self.reconstructor = DocumentReconstructor(self)
        self.rag_integration = RAGDocumentGraphIntegration(self)
    
    # Exponer métodos del analyzer
    def bfs_traversal(self, start_vertex: str, max_depth: int = 3):
        return self.analyzer.bfs_traversal(start_vertex, max_depth)
    
    def find_shortest_path(self, start: str, end: str):
        return self.analyzer.find_shortest_path(start, end)
    
    def get_connected_components(self):
        return self.analyzer.get_connected_components()
    
    def calculate_centrality_measures(self):
        return self.analyzer.calculate_centrality_measures()
    
    def topological_sort(self):
        return self.analyzer.topological_sort()
    
    def detect_cycles(self):
        return self.analyzer.detect_cycles()
    
    def find_critical_edges(self):
        return self.analyzer.find_critical_edges()
    
    # Exponer métodos del reconstructor
    def reconstruct_document_path(self, start_chunk: str, document_id: str = None):
        return self.reconstructor.reconstruct_document_path(start_chunk, document_id)
    
    def find_document_start_chunks(self):
        return self.reconstructor.find_document_start_chunks()
    
    def get_contextual_chunks(self, chunk_id: str, context_radius: int = 2):
        return self.reconstructor.get_contextual_chunks(chunk_id, context_radius)
    
    def reconstruct_full_document(self, start_chunk_id: str):
        return self.reconstructor.reconstruct_full_document(start_chunk_id)
    
    def get_document_summary(self, document_id: str = None, start_chunk: str = None):
        return self.reconstructor.get_document_summary(document_id, start_chunk)
    
    def navigate_document(self, current_chunk: str, direction: str = "next", steps: int = 1):
        return self.reconstructor.navigate_document(current_chunk, direction, steps)
    
    # Exponer métodos de integración RAG
    def build_document_graph_from_nodes(self, nodes, similarity_threshold: float = 0.7, preserve_document_order: bool = True):
        return self.rag_integration.build_document_graph_from_nodes(nodes, similarity_threshold, preserve_document_order)
    
    def enhanced_document_retrieval(self, query_node_id: str, context_radius: int = 2, include_semantic: bool = True, max_chunks: int = 10):
        return self.rag_integration.enhanced_document_retrieval(query_node_id, context_radius, include_semantic, max_chunks)
    
    def get_comprehensive_context(self, query_node_id: str, context_strategy: str = "adaptive"):
        return self.rag_integration.get_comprehensive_context(query_node_id, context_strategy)


# Funciones de conveniencia para crear grafos
def create_document_graph(directed: bool = True) -> DocumentGraphAugmentation:
    """Crear un nuevo grafo de documentos"""
    return DocumentGraphAugmentation(directed)

def create_document_graph_from_nodes(nodes, similarity_threshold: float = 0.7, preserve_document_order: bool = True) -> DocumentGraphAugmentation:
    """Crear un grafo de documentos directamente desde nodos de LlamaIndex"""
    graph = DocumentGraphAugmentation(directed=True)
    graph.build_document_graph_from_nodes(nodes, similarity_threshold, preserve_document_order)
    return graph


# Exportar todas las clases principales
__all__ = [
    'DocumentGraphAugmentation',
    'DocumentGraphCore', 
    'Edge', 
    'Vertex',
    'GraphAnalyzer',
    'DocumentReconstructor', 
    'RAGDocumentGraphIntegration',
    'create_document_graph',
    'create_document_graph_from_nodes'
]
