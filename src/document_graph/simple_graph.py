from typing import List, Dict, Optional, Tuple
import networkx as nx
from .core.graph_manager import GraphManager
from .core.graph_analyzer import GraphAnalyzer  


class SimpleDocumentGraph:
    """Interface principal para el grafo de documentos - Versión simplificada para RAG"""
    
    def __init__(self):
        """Inicializar grafo con componentes esenciales"""
        self._manager = GraphManager()
        self._analyzer = None  # Se crea lazy cuando se necesite
    
    # ========================================================================
    # FUNCIONES ESENCIALES PARA RAG
    # ========================================================================
    
    def add_chunk(self, chunk_id: str, content: str, metadata: Dict = None) -> None:
        """Agregar chunk al grafo"""
        self._manager.add_chunk(chunk_id, content, metadata)
        self._invalidate_analyzer()

    def connect_chunks(self, chunk1_id: str, chunk2_id: str, weight: float = 1.0) -> bool:
        """Conectar dos chunks"""
        result = self._manager.connect_chunks(chunk1_id, chunk2_id, weight)
        self._invalidate_analyzer()
        return result
    
    def get_chunk_content(self, chunk_id: str) -> Optional[str]:
        """Obtener contenido de un chunk"""
        return self._manager.get_chunk_content(chunk_id)
    
    def get_connected_chunks(self, chunk_id: str, max_connections: int = 5) -> List[Tuple[str, float]]:
        """Obtener chunks conectados directamente con sus pesos"""
        if not self.chunk_exists(chunk_id):
            return []
        
        connected = []
        for neighbor in self._manager.graph.neighbors(chunk_id):
            # Obtener peso de la conexión
            weight = self._manager.graph[chunk_id][neighbor].get('weight', 1.0)
            connected.append((neighbor, weight))
        
        # Ordenar por peso y limitar
        connected.sort(key=lambda x: x[1], reverse=True)
        return connected[:max_connections]
    
    def get_most_important_chunks(self, top_k: int = 5) -> List[Tuple[str, float]]:
        """Obtener chunks más importantes usando PageRank - ESENCIAL para RAG"""
        return self._get_analyzer().get_most_important_chunks(top_k)
    
    def get_chunk_neighbors(self, chunk_id: str, radius: int = 1) -> List[str]:
        """Obtener vecinos de un chunk - ESENCIAL para contexto"""
        return self._get_analyzer().get_chunk_neighbors(chunk_id, radius)
    
    def get_chunk_importance(self, chunk_id: str) -> Optional[float]:
        """Obtener importancia PageRank de un chunk específico"""
        if not self.chunk_exists(chunk_id):
            return None
        
        # Calcular PageRank para todo el grafo
        import networkx as nx
        if self._manager.chunk_count == 0:
            return 0.0
        
        try:
            pagerank_scores = nx.pagerank(self._manager.graph)
            return pagerank_scores.get(chunk_id, 0.0)
        except:
            return 0.0
    
    # ========================================================================
    # UTILIDADES BÁSICAS
    # ========================================================================
    
    def chunk_exists(self, chunk_id: str) -> bool:
        """Verificar si un chunk existe"""
        return self._manager.chunk_exists(chunk_id)
    
    @property
    def chunk_count(self) -> int:
        """Número total de chunks"""
        return self._manager.chunk_count
    
    def clear(self) -> None:
        """Limpiar el grafo completamente"""
        self._manager.clear()
        self._invalidate_analyzer()
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas del grafo"""
        return {
            'nodes': self._manager.chunk_count,
            'edges': self._manager.graph.number_of_edges(),
            'connected_components': len(list(nx.weakly_connected_components(self._manager.graph))) if self._manager.chunk_count > 0 else 0
        }
    
    # ========================================================================
    # MÉTODOS INTERNOS
    # ========================================================================
    
    def _get_analyzer(self) -> GraphAnalyzer:
        """Obtener analizador (lazy initialization)"""
        if self._analyzer is None:
            self._analyzer = GraphAnalyzer(self._manager.graph)
        return self._analyzer
    
    def _invalidate_analyzer(self) -> None:
        """Invalidar analyzer cached cuando el grafo cambia"""
        self._analyzer = None


# ============================================================================
# FUNCIÓN DE CONSTRUCCIÓN PARA RAG
# ============================================================================

def create_simple_rag_graph(documents_chunks: List[Dict]) -> SimpleDocumentGraph:
    """Crear grafo simple desde chunks de documentos - ESENCIAL para RAG"""
    from .utils.graph_builder import GraphBuilder
    
    if not documents_chunks:
        raise ValueError("No se proporcionaron chunks para construir el grafo")
    
    graph = SimpleDocumentGraph()
    builder = GraphBuilder(graph._manager)
    
    builder.build_from_chunks(documents_chunks)
    
    #| Grafo RAG creado exitosamente con {graph.chunk_count} chunks
    
    return graph
