"""
🌳 GRAFO JERÁRQUICO DE DOCUMENTOS
===============================

Implementación de la arquitectura jerárquica:
- Grafos individuales por documento (árboles)
- Meta-grafo conectando raíces
- Análisis jerárquico especializado
"""

from typing import List, Dict, Optional, Tuple
import networkx as nx
from .simple_graph import SimpleDocumentGraph
from .core.hierarchical_analyzer import HierarchicalGraphAnalyzer
from .utils.hierarchical_graph_builder import HierarchicalGraphBuilder


class HierarchicalDocumentGraph(SimpleDocumentGraph):
    """
    Grafo jerárquico que extiende SimpleDocumentGraph
    Mantiene compatibilidad pero agrega funcionalidad jerárquica
    """
    
    def __init__(self):
        """Inicializar grafo jerárquico"""
        super().__init__()
        self._hierarchical_analyzer = None
        self._document_roots = {}  # doc_name -> root_chunk_id
        self._document_graphs = {}  # doc_name -> list[chunk_ids]
        self._is_hierarchical = False
    
    # ========================================================================
    # CONSTRUCCIÓN JERÁRQUICA
    # ========================================================================
    
    def build_hierarchical(self, documents_chunks: List[Dict]) -> None:
        """Construir la arquitectura jerárquica"""
        builder = HierarchicalGraphBuilder(self._manager)
        builder.build_hierarchical_from_chunks(documents_chunks)
        
        # Extraer información jerárquica
        self._document_roots = builder.get_document_roots()
        self._document_graphs = {
            doc_name: builder.get_document_chunks(doc_name) 
            for doc_name in self._document_roots.keys()
        }
        self._is_hierarchical = True
        
        # Invalidar analyzers para que se reconstruyan
        self._invalidate_hierarchical_analyzer()
        
        print(f"✅ Arquitectura jerárquica configurada:")
        print(f"   📄 Documentos: {len(self._document_graphs)}")
        print(f"   🌿 Raíces: {list(self._document_roots.keys())}")
    
    # ========================================================================
    # ANÁLISIS JERÁRQUICO
    # ========================================================================
    
    def get_most_important_chunks_hierarchical(
        self, 
        top_k: int = 5, 
        strategy: str = "mixed"
    ) -> List[Tuple[str, float, str]]:
        """
        PageRank jerárquico con estrategias especializadas
        
        Args:
            top_k: Número de chunks a retornar
            strategy: "mixed", "roots_first", "within_docs", "meta_only"
        
        Returns:
            Lista de (chunk_id, score, document_name)
        """
        if not self._is_hierarchical:
            # Fallback a método normal si no es jerárquico
            normal_chunks = self.get_most_important_chunks(top_k)
            return [(chunk_id, score, "unknown") for chunk_id, score in normal_chunks]
        
        analyzer = self._get_hierarchical_analyzer()
        return analyzer.get_most_important_chunks_hierarchical(top_k, strategy)
    
    def get_document_context(self, chunk_id: str, context_size: int = 3) -> List[str]:
        """Obtener contexto dentro del mismo documento"""
        if not self._is_hierarchical:
            return self.get_chunk_neighbors(chunk_id, radius=1)
        
        analyzer = self._get_hierarchical_analyzer()
        return analyzer.get_document_context(chunk_id, context_size)
    
    def get_cross_document_context(self, chunk_id: str, max_docs: int = 2) -> List[str]:
        """Obtener contexto de otros documentos"""
        if not self._is_hierarchical:
            return []
        
        analyzer = self._get_hierarchical_analyzer()
        return analyzer.get_cross_document_context(chunk_id, max_docs)
    
    def get_enhanced_context(self, chunk_id: str, total_context: int = 5) -> Dict[str, List[str]]:
        """
        Obtener contexto enriquecido (intra-documento + inter-documento)
        
        Returns:
            {
                'same_document': [chunk_ids],
                'other_documents': [chunk_ids],
                'document_roots': [root_chunk_ids]
            }
        """
        context = {
            'same_document': [],
            'other_documents': [],
            'document_roots': []
        }
        
        if not self._is_hierarchical:
            context['same_document'] = self.get_chunk_neighbors(chunk_id, radius=1)
            return context
        
        # Distribución inteligente del contexto
        intra_doc_size = max(2, total_context // 2)
        inter_doc_size = total_context - intra_doc_size
        
        context['same_document'] = self.get_document_context(chunk_id, intra_doc_size)
        context['other_documents'] = self.get_cross_document_context(chunk_id, max_docs=2)
        context['document_roots'] = list(self._document_roots.values())
        
        return context
    
    # ========================================================================
    # CONSULTAS JERÁRQUICAS ESPECÍFICAS
    # ========================================================================
    
    def get_document_roots(self) -> Dict[str, str]:
        """Obtener raíces de todos los documentos"""
        return self._document_roots.copy()
    
    def get_documents_list(self) -> List[str]:
        """Obtener lista de nombres de documentos"""
        return list(self._document_graphs.keys())
    
    def get_chunks_by_document(self, doc_name: str) -> List[str]:
        """Obtener todos los chunks de un documento específico"""
        return self._document_graphs.get(doc_name, [])
    
    def find_document_for_chunk(self, chunk_id: str) -> Optional[str]:
        """Encontrar a qué documento pertenece un chunk"""
        for doc_name, chunks in self._document_graphs.items():
            if chunk_id in chunks:
                return doc_name
        return None
    
    def get_document_tree_stats(self, doc_name: str) -> Dict:
        """Estadísticas del árbol de un documento específico"""
        if doc_name not in self._document_graphs:
            return {}
        
        chunk_ids = self._document_graphs[doc_name]
        doc_subgraph = self._manager.graph.subgraph(chunk_ids)
        
        return {
            'document_name': doc_name,
            'total_chunks': len(chunk_ids),
            'root_chunk': self._document_roots.get(doc_name),
            'tree_edges': doc_subgraph.number_of_edges(),
            'tree_depth': self._calculate_tree_depth(doc_name),
            'is_connected': nx.is_connected(doc_subgraph.to_undirected())
        }
    
    def _calculate_tree_depth(self, doc_name: str) -> int:
        """Calcular profundidad máxima del árbol de documento"""
        if doc_name not in self._document_roots:
            return 0
        
        root_id = self._document_roots[doc_name]
        chunk_ids = self._document_graphs[doc_name]
        doc_subgraph = self._manager.graph.subgraph(chunk_ids)
        
        max_depth = 0
        for chunk_id in chunk_ids:
            if chunk_id != root_id:
                try:
                    path = nx.shortest_path(doc_subgraph, root_id, chunk_id)
                    depth = len(path) - 1
                    max_depth = max(max_depth, depth)
                except:
                    continue
        
        return max_depth
    
    # ========================================================================
    # ESTADÍSTICAS JERÁRQUICAS
    # ========================================================================
    
    def get_hierarchical_stats(self) -> Dict:
        """Estadísticas completas de la arquitectura jerárquica"""
        if not self._is_hierarchical:
            return self.get_stats()
        
        analyzer = self._get_hierarchical_analyzer()
        return analyzer.get_hierarchical_stats()
    
    def print_hierarchy_summary(self) -> None:
        """Imprimir resumen de la jerarquía"""
        if not self._is_hierarchical:
            print("⚠️  Grafo no es jerárquico")
            return
        
        print("\n🌳 RESUMEN DE ARQUITECTURA JERÁRQUICA")
        print("=" * 50)
        
        for doc_name, root_chunk in self._document_roots.items():
            chunks_count = len(self._document_graphs[doc_name])
            tree_stats = self.get_document_tree_stats(doc_name)
            
            print(f"📄 {doc_name}")
            print(f"   🌿 Raíz: {root_chunk}")
            print(f"   📊 Chunks: {chunks_count}")
            print(f"   📏 Profundidad: {tree_stats.get('tree_depth', 0)}")
            print(f"   🔗 Conexiones: {tree_stats.get('tree_edges', 0)}")
            print()
        
        stats = self.get_hierarchical_stats()
        print(f"🌐 META-GRAFO:")
        print(f"   🔗 Conexiones entre documentos: {stats.get('meta_graph_connections', 0)}")
        print(f"   📈 Conectividad cruzada: {stats.get('cross_document_connectivity', 0):.2%}")
        print("=" * 50)
    
    # ========================================================================
    # GESTIÓN DE ANALYZERS
    # ========================================================================
    
    def _get_hierarchical_analyzer(self) -> HierarchicalGraphAnalyzer:
        """Obtener analizador jerárquico (lazy initialization)"""
        if self._hierarchical_analyzer is None:
            self._hierarchical_analyzer = HierarchicalGraphAnalyzer(
                self._manager.graph,
                self._document_roots,
                self._document_graphs
            )
        return self._hierarchical_analyzer
    
    def _invalidate_hierarchical_analyzer(self) -> None:
        """Invalidar analyzer jerárquico cuando el grafo cambia"""
        self._hierarchical_analyzer = None
        super()._invalidate_analyzer()  # También invalidar el analyzer base
    
    # ========================================================================
    # COMPATIBILIDAD CON SimpleDocumentGraph
    # ========================================================================
    
    def get_stats(self) -> Dict:
        """Override para incluir información jerárquica si está disponible"""
        if self._is_hierarchical:
            return self.get_hierarchical_stats()
        else:
            return super().get_stats()
    
    @property
    def is_hierarchical(self) -> bool:
        """Verificar si el grafo usa arquitectura jerárquica"""
        return self._is_hierarchical


# ============================================================================
# FUNCIÓN DE CONSTRUCCIÓN JERÁRQUICA
# ============================================================================

def create_hierarchical_rag_graph(documents_chunks: List[Dict]) -> HierarchicalDocumentGraph:
    """
    Crear grafo jerárquico desde chunks de documentos
    
    Args:
        documents_chunks: Lista de chunks con metadata de documento
    
    Returns:
        HierarchicalDocumentGraph configurado
    """
    if not documents_chunks:
        raise ValueError("No se proporcionaron chunks para construir el grafo jerárquico")
    
    graph = HierarchicalDocumentGraph()
    graph.build_hierarchical(documents_chunks)
    
    print(f"🌳 Grafo jerárquico RAG creado con {graph.chunk_count} chunks")
    graph.print_hierarchy_summary()
    
    return graph