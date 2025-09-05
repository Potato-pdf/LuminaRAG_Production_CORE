"""
Integración específica del sistema de grafos con LlamaIndex RAG.
Maneja la construcción del grafo desde nodos de LlamaIndex y la recuperación mejorada.
"""
from typing import List, Dict, Set, Optional, Any, Tuple
from collections import defaultdict
from llama_index.core.schema import Node

from .graph_core import DocumentGraphCore, Edge
from .graph_algorithms import GraphAnalyzer
from .document_reconstructor import DocumentReconstructor


class RAGDocumentGraphIntegration:
    """Clase para integrar el grafo dirigido con el sistema RAG para reconstrucción de documentos"""
    
    def __init__(self, graph: DocumentGraphCore):
        self.graph = graph
        self.analyzer = GraphAnalyzer(graph)
        self.reconstructor = DocumentReconstructor(graph)
    
    def build_document_graph_from_nodes(self, nodes: List[Node], 
                                      similarity_threshold: float = 0.7,
                                      preserve_document_order: bool = True):
        """
        Construir grafo dirigido a partir de nodos de LlamaIndex preservando orden de documento
        
        Args:
            nodes: Lista de nodos de LlamaIndex
            similarity_threshold: Umbral para aristas semánticas
            preserve_document_order: Si preservar el orden original del documento
        """
        print(f"Construyendo grafo de documentos con {len(nodes)} nodos...")
        
        # Agregar todos los nodos como vértices
        for i, node in enumerate(nodes):
            metadata = {
                'content': node.get_content(),
                'node_id': node.node_id,
                'metadata': node.metadata,
                'document_position': self._extract_document_position(node),
                'creation_index': i
            }
            self.graph.add_vertex(node.node_id, metadata)
        
        if preserve_document_order:
            # Agrupar nodos por documento y crear aristas secuenciales
            docs_nodes = self._group_nodes_by_document(nodes)
            
            for doc_id, doc_nodes in docs_nodes.items():
                print(f"Procesando documento {doc_id} con {len(doc_nodes)} chunks...")
                
                # Ordenar nodos por posición en el documento
                doc_nodes.sort(key=lambda n: self._extract_document_position(n))
                
                # Crear secuencia de chunks para este documento
                chunk_sequence = [node.node_id for node in doc_nodes]
                self.graph.add_sequential_edges(chunk_sequence, weight=1.0)
        
        # Crear aristas semánticas basadas en similitud
        print("Creando aristas semánticas...")
        semantic_edges_created = 0
        
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes[i+1:], i+1):
                similarity = self._calculate_similarity(node1, node2)
                
                if similarity > similarity_threshold:
                    # Crear arista dirigida basada en posición en el documento
                    pos1 = self._extract_document_position(node1)
                    pos2 = self._extract_document_position(node2)
                    
                    if pos1 < pos2:
                        edge = Edge(node1.node_id, node2.node_id, similarity)
                        self.graph.add_edge(edge, similarity, "semantic")
                    else:
                        edge = Edge(node2.node_id, node1.node_id, similarity)
                        self.graph.add_edge(edge, similarity, "semantic")
                    
                    semantic_edges_created += 1
        
        print(f"Grafo construido exitosamente:")
        print(f"- Vértices: {self.graph.get_vertex_count()}")
        print(f"- Aristas totales: {self.graph.get_edge_count()}")
        print(f"- Aristas semánticas: {semantic_edges_created}")
    
    def _group_nodes_by_document(self, nodes: List[Node]) -> Dict[str, List[Node]]:
        """Agrupar nodos por documento de origen"""
        docs = defaultdict(list)
        
        for node in nodes:
            # Extraer ID del documento desde metadatos o nombre del archivo
            doc_id = node.metadata.get('file_name', 
                    node.metadata.get('source', 
                    node.metadata.get('filename', 'unknown_doc')))
            docs[doc_id].append(node)
        
        return dict(docs)
    
    def _extract_document_position(self, node: Node) -> int:
        """Extraer la posición del nodo en el documento original"""
        # Intentar extraer posición desde metadatos
        position = node.metadata.get('position', 
                  node.metadata.get('chunk_index',
                  node.metadata.get('start_char_idx', 0)))
        
        if isinstance(position, int):
            return position
        
        # Fallback: usar hash del contenido para ordenamiento consistente
        return hash(node.get_content()[:100]) % 1000000
    
    def _calculate_similarity(self, node1: Node, node2: Node) -> float:
        """Calcular similitud entre dos nodos"""
        # Similitud basada en palabras comunes (implementación básica)
        content1 = set(node1.get_content().lower().split())
        content2 = set(node2.get_content().lower().split())
        
        if not content1 or not content2:
            return 0.0
        
        intersection = len(content1.intersection(content2))
        union = len(content1.union(content2))
        
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # Bonus por metadatos similares
        metadata_bonus = 0.0
        if (node1.metadata.get('file_name') == node2.metadata.get('file_name') and
            node1.metadata.get('file_name') is not None):
            metadata_bonus = 0.1
        
        return min(jaccard_similarity + metadata_bonus, 1.0)
    
    def enhanced_document_retrieval(self, query_node_id: str, 
                                  context_radius: int = 2,
                                  include_semantic: bool = True,
                                  max_chunks: int = 10) -> Dict[str, Any]:
        """
        Recuperación mejorada que reconstruye contexto de documento
        
        Args:
            query_node_id: ID del nodo de consulta
            context_radius: Radio de contexto secuencial
            include_semantic: Si incluir chunks relacionados semánticamente
            max_chunks: Máximo número de chunks a retornar
            
        Returns:
            Diccionario con chunks organizados por tipo de relación
        """
        result = {
            'query_node': query_node_id,
            'sequential_context': {},
            'semantic_related': [],
            'document_path': [],
            'centrality_scores': {},
            'document_summary': {}
        }
        
        # Obtener contexto secuencial
        result['sequential_context'] = self.reconstructor.get_contextual_chunks(
            query_node_id, context_radius
        )
        
        # Obtener camino completo del documento
        try:
            result['document_path'] = self.reconstructor.reconstruct_document_path(query_node_id)
        except Exception as e:
            print(f"Error reconstruyendo documento: {e}")
            result['document_path'] = [query_node_id]
        
        # Obtener chunks relacionados semánticamente si se solicita
        if include_semantic:
            semantic_successors = self.graph.get_successors(query_node_id, "semantic")
            semantic_predecessors = self.graph.get_predecessors(query_node_id, "semantic")
            
            all_semantic = semantic_successors + [{'vertex': p, 'weight': 0.5} 
                                                for p in semantic_predecessors]
            
            # Ordenar por peso y tomar los mejores
            all_semantic.sort(key=lambda x: x.get('weight', 0), reverse=True)
            result['semantic_related'] = [
                item['vertex'] if isinstance(item, dict) else item 
                for item in all_semantic[:max_chunks//2]
            ]
        
        # Calcular scores de centralidad para priorización
        try:
            centralities = self.analyzer.calculate_centrality_measures()
            result['centrality_scores'] = centralities.get(query_node_id, {})
        except Exception as e:
            print(f"Error calculando centralidad: {e}")
            result['centrality_scores'] = {}
        
        # Obtener resumen del documento
        try:
            result['document_summary'] = self.reconstructor.get_document_summary(
                start_chunk=query_node_id
            )
        except Exception as e:
            print(f"Error obteniendo resumen: {e}")
            result['document_summary'] = {}
        
        return result
    
    def get_comprehensive_context(self, query_node_id: str, 
                                context_strategy: str = "adaptive") -> List[Dict[str, Any]]:
        """
        Obtener contexto comprensivo usando diferentes estrategias
        
        Args:
            query_node_id: ID del nodo de consulta
            context_strategy: "sequential", "semantic", "adaptive", "full_document"
            
        Returns:
            Lista de chunks con información contextual y scores
        """
        context_chunks = []
        
        if context_strategy == "sequential":
            # Solo contexto secuencial
            context = self.reconstructor.get_contextual_chunks(query_node_id, context_radius=3)
            all_chunks = context['before'] + [context['current']] + context['after']
            
            for i, chunk_id in enumerate(all_chunks):
                context_chunks.append({
                    'chunk_id': chunk_id,
                    'type': 'sequential',
                    'position': i - len(context['before']),
                    'score': 1.0 - abs(i - len(context['before'])) * 0.1,
                    'metadata': self.graph.vertex_metadata.get(chunk_id, {})
                })
        
        elif context_strategy == "semantic":
            # Solo relaciones semánticas
            enhanced_result = self.enhanced_document_retrieval(
                query_node_id, context_radius=1, include_semantic=True
            )
            
            for chunk_id in enhanced_result['semantic_related']:
                # Encontrar el peso de la relación semántica
                successors = self.graph.get_successors(query_node_id, "semantic")
                weight = next((s['weight'] for s in successors if s['vertex'] == chunk_id), 0.5)
                
                context_chunks.append({
                    'chunk_id': chunk_id,
                    'type': 'semantic',
                    'position': 0,
                    'score': weight,
                    'metadata': self.graph.vertex_metadata.get(chunk_id, {})
                })
        
        elif context_strategy == "adaptive":
            # Combinar ambas estrategias adaptativamente
            enhanced_result = self.enhanced_document_retrieval(
                query_node_id, context_radius=2, include_semantic=True
            )
            
            # Agregar contexto secuencial con peso alto
            context = enhanced_result['sequential_context']
            all_sequential = context['before'] + [context['current']] + context['after']
            
            for i, chunk_id in enumerate(all_sequential):
                context_chunks.append({
                    'chunk_id': chunk_id,
                    'type': 'sequential',
                    'position': i - len(context['before']),
                    'score': 0.9 - abs(i - len(context['before'])) * 0.1,
                    'metadata': self.graph.vertex_metadata.get(chunk_id, {})
                })
            
            # Agregar relaciones semánticas con peso moderado
            for chunk_id in enhanced_result['semantic_related']:
                if chunk_id not in [c['chunk_id'] for c in context_chunks]:
                    successors = self.graph.get_successors(query_node_id, "semantic")
                    weight = next((s['weight'] for s in successors if s['vertex'] == chunk_id), 0.5)
                    
                    context_chunks.append({
                        'chunk_id': chunk_id,
                        'type': 'semantic',
                        'position': 0,
                        'score': weight * 0.7,  # Reducir peso semántico
                        'metadata': self.graph.vertex_metadata.get(chunk_id, {})
                    })
        
        elif context_strategy == "full_document":
            # Documento completo
            document_chunks = self.reconstructor.reconstruct_full_document(query_node_id)
            
            for chunk_info in document_chunks:
                context_chunks.append({
                    'chunk_id': chunk_info['chunk_id'],
                    'type': 'document',
                    'position': chunk_info['position'],
                    'score': 1.0 if chunk_info['chunk_id'] == query_node_id else 0.8,
                    'metadata': chunk_info['metadata']
                })
        
        # Ordenar por score y eliminar duplicados
        seen_chunks = set()
        unique_chunks = []
        
        for chunk in sorted(context_chunks, key=lambda x: x['score'], reverse=True):
            if chunk['chunk_id'] not in seen_chunks:
                unique_chunks.append(chunk)
                seen_chunks.add(chunk['chunk_id'])
        
        return unique_chunks
