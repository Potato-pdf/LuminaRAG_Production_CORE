
from typing import List, Dict
from ..core.graph_manager import GraphManager

class GraphBuilder:
   
    def __init__(self, graph_manager: GraphManager):
        self._manager = graph_manager
    
    def build_from_chunks(self, documents_chunks: List[Dict]) -> None:
        self._add_chunks_to_graph(documents_chunks)
        
        self._create_document_connections(documents_chunks)
        
        print("✅ Construcción del grafo completada")
    
    def _add_chunks_to_graph(self, documents_chunks: List[Dict]) -> None:
        for chunk_data in documents_chunks:
            self._validate_chunk_data(chunk_data)
            self._manager.add_chunk(
                chunk_id=chunk_data['id'],
                content=chunk_data['content'],
                metadata=chunk_data.get('metadata', {})
            )
    
    def _create_document_connections(self, documents_chunks: List[Dict]) -> None:
        docs_chunks = self._group_chunks_by_document(documents_chunks)
        
        for doc_name, chunk_ids in docs_chunks.items():
            self._create_sequential_connections(chunk_ids)
    
    def _validate_chunk_data(self, chunk_data: Dict) -> None:
        # Aceptar tanto 'id' como 'chunk_id' para flexibilidad
        if 'id' not in chunk_data and 'chunk_id' not in chunk_data:
            raise ValueError(f"Chunk data debe contener 'id' o 'chunk_id': {chunk_data}")
        
        if 'content' not in chunk_data:
            raise ValueError(f"Chunk data debe contener 'content': {chunk_data}")
        
        # Normalizar el ID
        chunk_id = chunk_data.get('id') or chunk_data.get('chunk_id')
        if not chunk_id or not chunk_id.strip():
            raise ValueError("El ID del chunk no puede estar vacío")
        
        if not chunk_data['content'].strip():
            raise ValueError("El contenido del chunk no puede estar vacío")
        
        # Asegurar que siempre tengamos 'id' para el resto del código
        if 'id' not in chunk_data:
            chunk_data['id'] = chunk_data['chunk_id']
    
    def _group_chunks_by_document(self, documents_chunks: List[Dict]) -> Dict[str, List[str]]:
        docs_chunks = {}
        
        for chunk_data in documents_chunks:
            doc_name = chunk_data.get('metadata', {}).get('file_name', 'unknown_document')
            if doc_name not in docs_chunks:
                docs_chunks[doc_name] = []
            docs_chunks[doc_name].append(chunk_data['id'])
        
        return docs_chunks
    
    def _create_sequential_connections(self, chunk_ids: List[str]) -> None:
        for i in range(len(chunk_ids) - 1):
            self._manager.connect_chunks(chunk_ids[i], chunk_ids[i + 1], weight=1.0)
    
    def add_similarity_connections(
        self, 
        similarity_threshold: float = 0.7,
        max_connections: int = 5
    ) -> None:
        print("   ⚠️  Funcionalidad no implementada aún - requiere modelo de embeddings")
        # TODO: Implementar cuando tengamos servicio de embeddings
    
    def build_custom_topology(self, connection_strategy: str = "sequential") -> None:
        if connection_strategy == "sequential":
            print("   ✅ Conexiones secuenciales ya aplicadas")
        elif connection_strategy == "hub":
            self._create_hub_topology()
        elif connection_strategy == "mesh":
            self._create_mesh_topology()
        else:
            print(f"   ⚠️  Estrategia '{connection_strategy}' no reconocida")
    
    def _create_hub_topology(self) -> None:
        print("   🌟 Creando topología hub...")
        # TODO: Implementar topología hub
        print("   ⚠️  Topología hub no implementada aún")
    
    def _create_mesh_topology(self) -> None:
        print("   🕸️  Creando topología mesh...")
        # TODO: Implementar topología mesh
        print("   ⚠️  Topología mesh no implementada aún")

def create_simple_rag_graph(documents_chunks: List[Dict]):
    from ..simple_graph import SimpleDocumentGraph
    
    if not documents_chunks:
        raise ValueError("No se proporcionaron chunks para construir el grafo")
    graph = SimpleDocumentGraph()
    builder = GraphBuilder(graph._manager)

    builder.build_from_chunks(documents_chunks)
    graph.get_stats()
    
    return graph
