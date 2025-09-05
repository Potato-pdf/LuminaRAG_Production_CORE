from typing import List, Dict, Optional, Tuple
from .core.graph_manager import GraphManager
from .core.graph_analyzer import GraphAnalyzer  
from .core.graph_exporter import GraphExporter

class SimpleDocumentGraph:#|Interface principal para el grafo de documentos
    def __init__(self):
        """Inicializar grafo con todos sus componentes"""
        # Componentes especializados
        self._manager = GraphManager()
        self._analyzer = None  # Se crea lazy cuando se necesite
        self._exporter = None  # Se crea lazy cuando se necesite

    def add_chunk(self, chunk_id: str, content: str, metadata: Dict = None) -> None:#|Agregar chunk al grafo
        self._manager.add_chunk(chunk_id, content, metadata)
        self._invalidate_analyzers()  # Invalidar analizadores cached

    def connect_chunks(self, chunk1_id: str, chunk2_id: str, weight: float = 1.0) -> bool:#|Conectar dos chunks
        result = self._manager.connect_chunks(chunk1_id, chunk2_id, weight)
        self._invalidate_analyzers()  # Invalidar analizadores cached
        return result
    
    def get_chunk_content(self, chunk_id: str) -> Optional[str]:
        """Obtener contenido de un chunk"""
        return self._manager.get_chunk_content(chunk_id)
    
    def get_connected_chunks(self, chunk_id: str) -> List[str]:
        """Obtener chunks conectados directamente"""
        return self._manager.get_connected_chunks(chunk_id)
    
    def chunk_exists(self, chunk_id: str) -> bool:
        """Verificar si un chunk existe"""
        return self._manager.chunk_exists(chunk_id)

    def find_path(self, start_chunk: str, end_chunk: str) -> Optional[List[str]]:
        """Encontrar camino más corto entre chunks"""
        return self._get_analyzer().find_path(start_chunk, end_chunk)
    
    def get_most_important_chunks(self, top_k: int = 5) -> List[Tuple[str, float]]:
        """Obtener chunks más importantes usando PageRank"""
        return self._get_analyzer().get_most_important_chunks(top_k)
    
    def get_chunk_neighbors(self, chunk_id: str, radius: int = 1) -> List[str]:
        """Obtener vecinos de un chunk"""
        return self._get_analyzer().get_chunk_neighbors(chunk_id, radius)
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas del grafo"""
        return self._get_analyzer().get_stats()
    
    def analyze_connectivity(self, chunk_id: str) -> Dict:
        """Analizar conectividad de un chunk específico"""
        return self._get_analyzer().analyze_connectivity(chunk_id)
    
    def save_graph(self, filename: str) -> None:
        """Guardar grafo en múltiples formatos"""
        self._get_exporter().save_graph(filename)
    
    def export_to_dict(self) -> Dict:
        """Exportar grafo a diccionario"""
        return self._get_exporter().export_to_dict()
    
    def save_subset(self, filename: str, chunk_ids: List[str]) -> None:
        """Guardar subconjunto del grafo"""
        self._get_exporter().save_subset(filename, chunk_ids)
    
    def export_statistics_report(self, filename: str) -> None:
        """Exportar reporte de estadísticas"""
        self._get_exporter().export_statistics_report(filename)
 
    def _get_analyzer(self) -> GraphAnalyzer:
        """Obtener analizador (lazy initialization)"""
        if self._analyzer is None:
            self._analyzer = GraphAnalyzer(self._manager.graph)
        return self._analyzer
    
    def _get_exporter(self) -> GraphExporter:
        """Obtener exportador (lazy initialization)"""
        if self._exporter is None:
            self._exporter = GraphExporter(self._manager.graph)
        return self._exporter
    
    def _invalidate_analyzers(self) -> None:
        """Invalidar analyzers cached cuando el grafo cambia"""
        self._analyzer = None
        self._exporter = None
    
    def clear(self) -> None:
        """Limpiar el grafo completamente"""
        self._manager.clear()
        self._invalidate_analyzers()
    
    @property
    def chunk_count(self) -> int:
        """Número total de chunks"""
        return self._manager.chunk_count
   
    def _chunk_exists(self, chunk_id: str) -> bool:
        """Método privado de compatibilidad"""
        return self.chunk_exists(chunk_id)

def create_simple_rag_graph(documents_chunks: List[Dict]) -> SimpleDocumentGraph:
    from .utils.graph_builder import GraphBuilder
    
    if not documents_chunks:
        raise ValueError("No se proporcionaron chunks para construir el grafo")
    
    graph = SimpleDocumentGraph()
    builder = GraphBuilder(graph._manager)
    
    builder.build_from_chunks(documents_chunks)
    
    graph.get_stats()
    
    return graph
