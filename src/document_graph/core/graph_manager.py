import networkx as nx
from typing import Dict, Optional


class GraphManager:#Gestor del grafo, maneja operaciones basicas
    def __init__(self):
        self._graph = nx.DiGraph()
        self._chunk_count = 0
    @property#|Acceso al grafo NetworkX (solo lectura desde exterior)
    def graph(self) -> nx.DiGraph:
        return self._graph

    @property#|Número total de chunks
    def chunk_count(self) -> int:
        return self._chunk_count
    
    def add_chunk(self, chunk_id: str, content: str, metadata: Dict = None) -> None:
        #| Agrega un chunk al grafo con su contenido y metadatos
        if metadata is None:
            metadata = {}
        if self.chunk_exists(chunk_id):
            raise ValueError(f"Chunk {chunk_id} ya existe en el grafo")
        self._graph.add_node(
            chunk_id,
            content=content,
            metadata=metadata
        )
        self._chunk_count += 1
        #| Chunk agregado exitosamente - Total: {self._chunk_count}
        
    def connect_chunks(self, chunk1_id: str, chunk2_id: str, weight: float = 1.0) -> bool:
        #| Conecta dos chunks en el grafo con peso especificado
        if not self.chunk_exists(chunk1_id):
            #| Error: chunk {chunk1_id} no existe
            return False
            
        if not self.chunk_exists(chunk2_id):
            #| Error: chunk {chunk2_id} no existe
            return False
            
        self._graph.add_edge(chunk1_id, chunk2_id, weight=weight)
        #| Chunks conectados: {chunk1_id} → {chunk2_id} (peso: {weight})
        return True

    def get_chunk_content(self, chunk_id: str) -> Optional[str]:
        #| Obtiene el contenido de un chunk específico
        if self.chunk_exists(chunk_id):
            return self._graph.nodes[chunk_id]['content']
        else:
            #| Chunk {chunk_id} no encontrado
            return None
    
    def get_chunk_metadata(self, chunk_id: str) -> Optional[Dict]:#|Obtiene los metadatos de un chunk
        if self.chunk_exists(chunk_id):
            return self._graph.nodes[chunk_id]['metadata']
        else:
            print(f"❌ Chunk {chunk_id} no encontrado")
            return None
    
    def chunk_exists(self, chunk_id: str) -> bool:#|Verifica si un chunk existe en el grafo
        return chunk_id in self._graph
    
    def get_connected_chunks(self, chunk_id: str) -> list[str]:#|Obtiene los chunks conectados directamente a un chunk dado
        if not self.chunk_exists(chunk_id):
            print(f"❌ Chunk {chunk_id} no encontrado")
            return []
            
        connected = list(self._graph.successors(chunk_id))
        print(f"🔍 Chunks conectados desde {chunk_id}: {connected}")
        return connected
    
    def clear(self) -> None:#|Limpia el grafo completamente
        """Limpiar el grafo completamente"""
        self._graph.clear()
        self._chunk_count = 0
        print("🧹 Grafo limpiado completamente")
