"""
🧠 ANALIZADOR DE GRAFOS JERÁRQUICOS
==================================

Analizador especializado para la arquitectura jerárquica:
- Análisis por documento individual
- Análisis del meta-grafo
- PageRank jerárquico
"""

import networkx as nx
from typing import List, Tuple, Dict, Optional, Set
from .graph_analyzer import GraphAnalyzer


class HierarchicalGraphAnalyzer(GraphAnalyzer):
    """Analizador para grafos jerárquicos - Extiende GraphAnalyzer base"""
    
    def __init__(self, graph: nx.DiGraph, document_roots: Dict[str, str], document_graphs: Dict[str, List[str]]):
        super().__init__(graph)
        self._document_roots = document_roots
        self._document_graphs = document_graphs
    
    # ========================================================================
    # ANÁLISIS JERÁRQUICO ESPECIALIZADO
    # ========================================================================
    
    def get_most_important_chunks_hierarchical(self, top_k: int = 5, strategy: str = "mixed") -> List[Tuple[str, float, str]]:
        """
        PageRank jerárquico con diferentes estrategias
        
        Args:
            top_k: Número de chunks a retornar
            strategy: "mixed", "roots_first", "within_docs", "meta_only"
        
        Returns:
            Lista de (chunk_id, score, document_name)
        """
        if strategy == "roots_first":
            return self._get_roots_first_ranking(top_k)
        elif strategy == "within_docs":
            return self._get_within_docs_ranking(top_k)
        elif strategy == "meta_only":
            return self._get_meta_graph_ranking(top_k)
        else:  # mixed (default)
            return self._get_mixed_hierarchical_ranking(top_k)
    
    def _get_roots_first_ranking(self, top_k: int) -> List[Tuple[str, float, str]]:
        """Priorizar raíces de documentos"""
        pagerank_scores = nx.pagerank(self._graph)
        results = []
        
        # Primero agregar todas las raíces
        for doc_name, root_id in self._document_roots.items():
            score = pagerank_scores.get(root_id, 0.0)
            results.append((root_id, score * 1.5, doc_name))  # Boost para raíces
        
        # Luego agregar chunks no-raíz más importantes
        non_root_chunks = []
        for chunk_id, score in pagerank_scores.items():
            if chunk_id not in self._document_roots.values():
                doc_name = self._get_document_for_chunk(chunk_id)
                non_root_chunks.append((chunk_id, score, doc_name))
        
        # Ordenar no-raíz por score
        non_root_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Combinar respetando top_k
        remaining_slots = top_k - len(results)
        if remaining_slots > 0:
            results.extend(non_root_chunks[:remaining_slots])
        
        return results[:top_k]
    
    def _get_within_docs_ranking(self, top_k: int) -> List[Tuple[str, float, str]]:
        """Ranking distribuido: mejor chunk de cada documento"""
        results = []
        chunks_per_doc = max(1, top_k // len(self._document_graphs))
        
        for doc_name, chunk_ids in self._document_graphs.items():
            # Crear subgrafo del documento
            doc_subgraph = self._graph.subgraph(chunk_ids)
            
            if doc_subgraph.number_of_nodes() > 0:
                doc_pagerank = nx.pagerank(doc_subgraph)
                doc_chunks = sorted(doc_pagerank.items(), key=lambda x: x[1], reverse=True)
                
                # Tomar los mejores chunks de este documento
                for chunk_id, score in doc_chunks[:chunks_per_doc]:
                    results.append((chunk_id, score, doc_name))
        
        # Ordenar globalmente y tomar top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _get_meta_graph_ranking(self, top_k: int) -> List[Tuple[str, float, str]]:
        """Solo considerar el meta-grafo (raíces)"""
        root_ids = list(self._document_roots.values())
        meta_subgraph = self._graph.subgraph(root_ids)
        
        if meta_subgraph.number_of_nodes() == 0:
            return []
        
        meta_pagerank = nx.pagerank(meta_subgraph)
        results = []
        
        for root_id, score in meta_pagerank.items():
            doc_name = self._get_document_for_chunk(root_id)
            results.append((root_id, score, doc_name))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _get_mixed_hierarchical_ranking(self, top_k: int) -> List[Tuple[str, float, str]]:
        """Estrategia mixta: combina PageRank global con boost jerárquico"""
        pagerank_scores = nx.pagerank(self._graph)
        results = []
        
        for chunk_id, base_score in pagerank_scores.items():
            doc_name = self._get_document_for_chunk(chunk_id)
            
            # Aplicar boost jerárquico
            hierarchical_score = self._calculate_hierarchical_boost(chunk_id, base_score)
            results.append((chunk_id, hierarchical_score, doc_name))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _calculate_hierarchical_boost(self, chunk_id: str, base_score: float) -> float:
        """Calcular boost jerárquico basado en posición en la jerarquía"""
        boost = 1.0
        
        # Boost para raíces de documentos
        if chunk_id in self._document_roots.values():
            boost += 0.5
        
        # Boost por conectividad en meta-grafo
        metadata = self._graph.nodes.get(chunk_id, {})
        if metadata.get('in_meta_graph', False):
            boost += 0.3
        
        # Boost por profundidad en el árbol (menos profundo = más importante)
        depth = self._calculate_tree_depth(chunk_id)
        if depth is not None:
            boost += max(0, (3 - depth) * 0.1)  # Menos boost a mayor profundidad
        
        return base_score * boost
    
    def _calculate_tree_depth(self, chunk_id: str) -> Optional[int]:
        """Calcular profundidad de un chunk en su árbol de documento"""
        doc_name = self._get_document_for_chunk(chunk_id)
        if not doc_name or doc_name not in self._document_roots:
            return None
        
        root_id = self._document_roots[doc_name]
        doc_chunks = self._document_graphs[doc_name]
        doc_subgraph = self._graph.subgraph(doc_chunks)
        
        try:
            path = nx.shortest_path(doc_subgraph, root_id, chunk_id)
            return len(path) - 1  # Profundidad = longitud del camino - 1
        except:
            return None
    
    # ========================================================================
    # ANÁLISIS CONTEXTUAL JERÁRQUICO
    # ========================================================================
    
    def get_document_context(self, chunk_id: str, context_size: int = 3) -> List[str]:
        """Obtener contexto jerárquico de un chunk"""
        doc_name = self._get_document_for_chunk(chunk_id)
        if not doc_name:
            return []
        
        # Obtener chunks del mismo documento
        doc_chunks = self._document_graphs[doc_name]
        doc_subgraph = self._graph.subgraph(doc_chunks)
        
        # Usar ego_graph para obtener vecinos cercanos en el documento
        try:
            ego = nx.ego_graph(doc_subgraph, chunk_id, radius=2)
            context_chunks = list(ego.nodes())
            
            # Remover el chunk central
            if chunk_id in context_chunks:
                context_chunks.remove(chunk_id)
            
            # Limitar tamaño
            return context_chunks[:context_size]
        except:
            return []
    
    def get_cross_document_context(self, chunk_id: str, max_docs: int = 2) -> List[str]:
        """Obtener contexto de otros documentos vía meta-grafo"""
        current_doc = self._get_document_for_chunk(chunk_id)
        if not current_doc:
            return []
        
        current_root = self._document_roots.get(current_doc)
        if not current_root:
            return []
        
        # Encontrar raíces conectadas en meta-grafo
        connected_roots = []
        for neighbor in self._graph.neighbors(current_root):
            if neighbor in self._document_roots.values() and neighbor != current_root:
                connected_roots.append(neighbor)
        
        # Obtener chunks representativos de documentos conectados
        cross_context = []
        for root in connected_roots[:max_docs]:
            # Agregar la raíz y algunos chunks importantes del documento
            cross_context.append(root)
            
            # Encontrar documento de esta raíz
            root_doc = self._get_document_for_chunk(root)
            if root_doc and root_doc in self._document_graphs:
                doc_chunks = self._document_graphs[root_doc][:2]  # Primeros 2 chunks
                cross_context.extend([c for c in doc_chunks if c != root])
        
        return cross_context[:max_docs * 3]  # Limitar total
    
    # ========================================================================
    # ESTADÍSTICAS JERÁRQUICAS
    # ========================================================================
    
    def get_hierarchical_stats(self) -> Dict:
        """Estadísticas de la arquitectura jerárquica"""
        base_stats = super().get_stats()
        
        hierarchical_stats = {
            'documents_count': len(self._document_graphs),
            'document_roots': len(self._document_roots),
            'meta_graph_connections': self._count_meta_connections(),
            'avg_chunks_per_document': self._calculate_avg_chunks_per_doc(),
            'document_tree_depths': self._calculate_tree_depths(),
            'cross_document_connectivity': self._calculate_cross_doc_connectivity()
        }
        
        # Combinar estadísticas
        base_stats.update(hierarchical_stats)
        return base_stats
    
    def _count_meta_connections(self) -> int:
        """Contar conexiones del meta-grafo"""
        root_ids = set(self._document_roots.values())
        meta_connections = 0
        
        for node1 in root_ids:
            for node2 in self._graph.neighbors(node1):
                if node2 in root_ids:
                    meta_connections += 1
        
        return meta_connections // 2  # Dividir por 2 porque contamos cada arista dos veces
    
    def _calculate_avg_chunks_per_doc(self) -> float:
        """Calcular promedio de chunks por documento"""
        if not self._document_graphs:
            return 0.0
        
        total_chunks = sum(len(chunks) for chunks in self._document_graphs.values())
        return total_chunks / len(self._document_graphs)
    
    def _calculate_tree_depths(self) -> Dict[str, int]:
        """Calcular profundidad máxima de cada árbol de documento"""
        depths = {}
        
        for doc_name, chunk_ids in self._document_graphs.items():
            if doc_name not in self._document_roots:
                continue
            
            root_id = self._document_roots[doc_name]
            doc_subgraph = self._graph.subgraph(chunk_ids)
            
            max_depth = 0
            for chunk_id in chunk_ids:
                if chunk_id != root_id:
                    try:
                        path = nx.shortest_path(doc_subgraph, root_id, chunk_id)
                        depth = len(path) - 1
                        max_depth = max(max_depth, depth)
                    except:
                        continue
            
            depths[doc_name] = max_depth
        
        return depths
    
    def _calculate_cross_doc_connectivity(self) -> float:
        """Calcular conectividad entre documentos"""
        if len(self._document_roots) < 2:
            return 0.0
        
        total_possible = len(self._document_roots) * (len(self._document_roots) - 1) // 2
        actual_connections = self._count_meta_connections()
        
        return actual_connections / total_possible if total_possible > 0 else 0.0
    
    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================
    
    def _get_document_for_chunk(self, chunk_id: str) -> Optional[str]:
        """Encontrar el documento al que pertenece un chunk"""
        for doc_name, chunks in self._document_graphs.items():
            if chunk_id in chunks:
                return doc_name
        return None