"""
🌳 CONSTRUCTOR DE GRAFOS JERÁRQUICOS
===================================

Construye una arquitectura de grafos jerárquica:
- 1 grafo por documento (árbol con raíz)
- 1 meta-grafo que conecta las raíces
"""

from typing import List, Dict, Set, Tuple
import networkx as nx
from ..core.graph_manager import GraphManager


class HierarchicalGraphBuilder:
    """Constructor de grafos jerárquicos - Un grafo por documento + meta-grafo"""
    
    def __init__(self, graph_manager: GraphManager):
        self._manager = graph_manager
        self._document_roots = {}  # doc_name -> root_chunk_id
        self._document_graphs = {}  # doc_name -> list[chunk_ids]
    
    def build_hierarchical_from_chunks(self, documents_chunks: List[Dict]) -> None:
        """Construye la arquitectura jerárquica completa"""
        print("🌳 Construyendo arquitectura jerárquica...")
        
        # 1. Agregar todos los chunks al grafo principal
        self._add_chunks_to_graph(documents_chunks)
        
        # 2. Agrupar chunks por documento
        docs_chunks = self._group_chunks_by_document(documents_chunks)
        
        # 3. Crear grafos individuales por documento (árboles)
        self._create_document_trees(docs_chunks)
        
        # 4. Crear meta-grafo conectando raíces
        self._create_meta_graph()
        
        print(f"✅ Arquitectura jerárquica creada:")
        print(f"   📄 {len(self._document_graphs)} documentos")
        print(f"   🌿 {len(self._document_roots)} raíces")
        print(f"   🔗 {sum(len(chunks) for chunks in self._document_graphs.values())} chunks totales")
    
    def _add_chunks_to_graph(self, documents_chunks: List[Dict]) -> None:
        """Agregar todos los chunks al grafo principal"""
        for chunk_data in documents_chunks:
            self._validate_chunk_data(chunk_data)
            self._manager.add_chunk(
                chunk_id=chunk_data['id'],
                content=chunk_data['content'],
                metadata=chunk_data.get('metadata', {})
            )
    
    def _group_chunks_by_document(self, documents_chunks: List[Dict]) -> Dict[str, List[str]]:
        """Agrupar chunks por documento"""
        docs_chunks = {}
        
        for chunk_data in documents_chunks:
            doc_name = chunk_data.get('metadata', {}).get('file_name', 'unknown_document')
            if doc_name not in docs_chunks:
                docs_chunks[doc_name] = []
            docs_chunks[doc_name].append(chunk_data['id'])
        
        return docs_chunks
    
    def _create_document_trees(self, docs_chunks: Dict[str, List[str]]) -> None:
        """Crear árboles individuales por documento"""
        for doc_name, chunk_ids in docs_chunks.items():
            print(f"   🌲 Creando árbol para: {doc_name}")
            
            if not chunk_ids:
                continue
            
            # Ordenar chunks por índice si está disponible
            sorted_chunks = self._sort_chunks_by_index(chunk_ids)
            
            # El primer chunk es la raíz del documento
            root_chunk = sorted_chunks[0]
            self._document_roots[doc_name] = root_chunk
            self._document_graphs[doc_name] = sorted_chunks
            
            # Marcar la raíz en metadata
            self._mark_as_root(root_chunk, doc_name)
            
            # Crear estructura de árbol
            self._create_tree_structure(sorted_chunks, doc_name)
    
    def _sort_chunks_by_index(self, chunk_ids: List[str]) -> List[str]:
        """Ordenar chunks por índice en metadata"""
        def get_chunk_index(chunk_id: str) -> int:
            metadata = self._manager.get_chunk_metadata(chunk_id)
            if metadata and 'chunk_index' in metadata:
                return metadata['chunk_index']
            return float('inf')  # Al final si no tiene índice
        
        return sorted(chunk_ids, key=get_chunk_index)
    
    def _mark_as_root(self, root_chunk_id: str, doc_name: str) -> None:
        """Marcar un chunk como raíz de documento"""
        metadata = self._manager.get_chunk_metadata(root_chunk_id)
        if metadata:
            metadata.update({
                'is_document_root': True,
                'document_name': doc_name,
                'node_type': 'document_root'
            })
    
    def _create_tree_structure(self, chunk_ids: List[str], doc_name: str) -> None:
        """Crear estructura de árbol para un documento"""
        if len(chunk_ids) < 2:
            return
        
        # Estrategia: árbol binario balanceado desde la raíz
        root = chunk_ids[0]
        remaining_chunks = chunk_ids[1:]
        
        # Conectar raíz con primeros chunks (nivel 1)
        level_size = min(3, len(remaining_chunks))  # Máximo 3 hijos directos
        for i in range(level_size):
            child = remaining_chunks[i]
            self._manager.connect_chunks(root, child, weight=1.0)
            print(f"      🔗 {root} → {child} (nivel 1)")
        
        # Crear niveles subsecuentes
        current_level = remaining_chunks[:level_size]
        remaining = remaining_chunks[level_size:]
        level_num = 2
        
        while remaining and current_level:
            next_level = []
            
            for parent in current_level:
                # Cada nodo puede tener 2-3 hijos
                children_count = min(2, len(remaining))
                for i in range(children_count):
                    if remaining:
                        child = remaining.pop(0)
                        self._manager.connect_chunks(parent, child, weight=1.0)
                        next_level.append(child)
                        print(f"      🔗 {parent} → {child} (nivel {level_num})")
            
            current_level = next_level
            level_num += 1
    
    def _create_meta_graph(self) -> None:
        """Crear meta-grafo conectando raíces de documentos"""
        root_chunks = list(self._document_roots.values())
        
        if len(root_chunks) < 2:
            print("   ⚠️  Solo hay 1 documento, no se crea meta-grafo")
            return
        
        print(f"   🌐 Creando meta-grafo con {len(root_chunks)} raíces...")
        
        # Conectar raíces en secuencia (puede cambiarse por otras estrategias)
        for i in range(len(root_chunks) - 1):
            root1 = root_chunks[i]
            root2 = root_chunks[i + 1]
            # Peso mayor para conexiones de meta-grafo
            self._manager.connect_chunks(root1, root2, weight=2.0)
            print(f"      🔗 META: {root1} ↔ {root2}")
        
        # Marcar conexiones del meta-grafo
        for root_chunk in root_chunks:
            metadata = self._manager.get_chunk_metadata(root_chunk)
            if metadata:
                metadata['in_meta_graph'] = True
    
    def _validate_chunk_data(self, chunk_data: Dict) -> None:
        """Validar datos de chunk"""
        if 'id' not in chunk_data and 'chunk_id' not in chunk_data:
            raise ValueError(f"Chunk data debe contener 'id' o 'chunk_id': {chunk_data}")
        
        if 'content' not in chunk_data:
            raise ValueError(f"Chunk data debe contener 'content': {chunk_data}")
        
        # Normalizar el ID
        chunk_id = chunk_data.get('id') or chunk_data.get('chunk_id')
        if not chunk_id or not chunk_id.strip():
            raise ValueError("El ID del chunk no puede estar vacío")
        
        # Asegurar que siempre tengamos 'id'
        if 'id' not in chunk_data:
            chunk_data['id'] = chunk_data['chunk_id']
    
    # ========================================================================
    # MÉTODOS DE CONSULTA PARA LA NUEVA ARQUITECTURA
    # ========================================================================
    
    def get_document_roots(self) -> Dict[str, str]:
        """Obtener raíces de todos los documentos"""
        return self._document_roots.copy()
    
    def get_document_chunks(self, doc_name: str) -> List[str]:
        """Obtener todos los chunks de un documento"""
        return self._document_graphs.get(doc_name, [])
    
    def get_root_for_chunk(self, chunk_id: str) -> str:
        """Encontrar la raíz del documento al que pertenece un chunk"""
        for doc_name, chunks in self._document_graphs.items():
            if chunk_id in chunks:
                return self._document_roots[doc_name]
        return None
    
    def get_document_for_chunk(self, chunk_id: str) -> str:
        """Encontrar el documento al que pertenece un chunk"""
        for doc_name, chunks in self._document_graphs.items():
            if chunk_id in chunks:
                return doc_name
        return None
    
    def get_meta_graph_connections(self) -> List[Tuple[str, str]]:
        """Obtener conexiones del meta-grafo"""
        connections = []
        roots = list(self._document_roots.values())
        
        for i in range(len(roots) - 1):
            connections.append((roots[i], roots[i + 1]))
        
        return connections