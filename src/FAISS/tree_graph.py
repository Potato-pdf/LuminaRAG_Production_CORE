import faiss
import numpy as np
from typing import Dict, List, Tuple, Optional
from .root_finder import RootFinder

class TreeGraphRAG:
    """
    🌳 RAG CON ARQUITECTURA FAISS + ÁRBOLES JERÁRQUICOS
    ==================================================
    
    Arquitectura optimizada:
    1. FAISS índice solo las raíces (ultra rápido)
    2. Búsqueda específica en árboles seleccionados
    3. Sin meta-grafo: completamente independiente
    """
    
    def __init__(self, embedding_model=None):
        self.root_finder = RootFinder(embedding_model)
        self.is_built = False
        
    def add_document(self, doc_id: str, hierarchical_graph, root_chunk_id: str):
        """
        Agregar documento al sistema FAISS + Trees
        
        Args:
            doc_id: Identificador del documento
            hierarchical_graph: Grafo jerárquico del documento
            root_chunk_id: ID del chunk raíz del documento
        """
        self.root_finder.add_document(doc_id, hierarchical_graph, root_chunk_id)
        self.is_built = False  # Requerir rebuild del índice
        
    def build_index(self) -> bool:
        """
        Construir el índice FAISS-GPU con todas las raíces
        
        Returns:
            True si se construyó exitosamente
        """
        print("\n🏗️ CONSTRUYENDO ÍNDICE FAISS-GPU...")
        print(f"🔍 GPUs detectadas: {faiss.get_num_gpus()}")
        
        success = self.root_finder.build_index()
        if success:
            self.is_built = True
            print("✅ Sistema FAISS-GPU + Trees listo")
        return success
        
    def search(self, query: str, k: int = 5, k_roots: int = 5) -> List[Tuple[str, float, str]]:
        """
        Búsqueda principal: FAISS + árboles específicos
        
        Flujo optimizado:
        1. FAISS encuentra top-k raíces más similares
        2. Búsqueda jerárquica solo en esos k árboles
        3. Combinación inteligente de scores
        
        Args:
            query: Consulta de texto
            k: Número de resultados finales
            k_roots: Número de raíces a considerar (default: 5)
            
        Returns:
            Lista de (chunk_id, combined_score, doc_id)
        """
        if not self.is_built:
            print("❌ Índice FAISS no construido. Ejecutar build_index() primero.")
            return []
            
        return self.root_finder.search(query, k, k_roots)
        
    def search_in_specific_documents(self, query: str, doc_ids: List[str], k: int = 5) -> List[Tuple[str, float, str]]:
        """
        Buscar solo en documentos específicos (sin FAISS)
        
        Args:
            query: Consulta de texto
            doc_ids: Lista de IDs de documentos donde buscar
            k: Número de resultados
            
        Returns:
            Lista de (chunk_id, score, doc_id)
        """
        results = []
        
        for doc_id in doc_ids:
            if doc_id not in self.root_finder.document_trees:
                print(f"⚠️ Documento no encontrado: {doc_id}")
                continue
                
            hierarchical_graph = self.root_finder.document_trees[doc_id]
            
            try:
                # Búsqueda jerárquica en el documento específico
                tree_results = hierarchical_graph.get_most_important_chunks_hierarchical(
                    top_k=k, 
                    strategy="mixed"
                )
                
                for chunk_id, score, chunk_doc in tree_results:
                    results.append((chunk_id, score, doc_id))
                    
            except Exception as e:
                print(f"❌ Error buscando en {doc_id}: {e}")
                
        # Ordenar por score
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
        
    def get_document_context(self, chunk_id: str, context_size: int = 3) -> List[str]:
        """
        Obtener contexto dentro del mismo documento
        
        Args:
            chunk_id: ID del chunk
            context_size: Tamaño del contexto
            
        Returns:
            Lista de chunk_ids relacionados
        """
        # Encontrar el documento que contiene el chunk
        for doc_id, hierarchical_graph in self.root_finder.document_trees.items():
            if hierarchical_graph.chunk_exists(chunk_id):
                return hierarchical_graph.get_document_context(chunk_id, context_size)
        
        return []
        
    def get_cross_document_context(self, chunk_id: str, query: str, max_docs: int = 2) -> List[str]:
        """
        Obtener contexto de otros documentos relevantes
        
        Args:
            chunk_id: Chunk de referencia
            query: Consulta para encontrar documentos relacionados
            max_docs: Número máximo de documentos a considerar
            
        Returns:
            Lista de chunk_ids de otros documentos
        """
        # Encontrar documentos relevantes con FAISS
        relevant_roots = self.root_finder.find_relevant_roots(query, max_docs)
        
        # Obtener chunks de esos documentos
        context_chunks = []
        for doc_id, score in relevant_roots:
            hierarchical_graph = self.root_finder.document_trees[doc_id]
            
            # Agregar chunks importantes del documento
            important_chunks = hierarchical_graph.get_most_important_chunks_hierarchical(
                top_k=2, strategy="roots_first"
            )
            
            for chunk, _, _ in important_chunks:
                if chunk != chunk_id:  # Evitar el chunk original
                    context_chunks.append(chunk)
                    
        return context_chunks[:5]  # Limitar contexto
        
    def get_stats(self) -> Dict:
        """
        Obtener estadísticas del sistema completo incluyendo GPU
        """
        base_stats = self.root_finder.get_stats()
        
        # Agregar estadísticas de árboles
        tree_stats = {
            'total_chunks': 0,
            'total_connections': 0,
            'average_tree_depth': 0
        }
        
        depths = []
        for doc_id, hierarchical_graph in self.root_finder.document_trees.items():
            stats = hierarchical_graph.get_hierarchical_stats()
            tree_stats['total_chunks'] += stats.get('total_chunks', 0)
            tree_stats['total_connections'] += stats.get('total_connections', 0)
            
            # Calcular profundidad promedio de árboles
            doc_stats = hierarchical_graph.get_document_tree_stats(doc_id)
            if 'tree_depth' in doc_stats:
                depths.append(doc_stats['tree_depth'])
                
        if depths:
            tree_stats['average_tree_depth'] = sum(depths) / len(depths)
        
        # Información de GPU
        gpu_stats = {
            'gpu_available': faiss.get_num_gpus() > 0,
            'gpu_count': faiss.get_num_gpus(),
            'index_type': 'GPU' if (hasattr(self.root_finder, 'index') and 
                                  hasattr(self.root_finder.index, 'device')) else 'CPU'
        }
            
        return {**base_stats, **tree_stats, **gpu_stats, 'is_built': self.is_built}
        
    def print_system_summary(self):
        """
        Imprimir resumen del sistema FAISS-GPU + Trees
        """
        stats = self.get_stats()
        
        print("\n🚀 SISTEMA FAISS-GPU + ÁRBOLES JERÁRQUICOS")
        print("=" * 50)
        print(f"📄 Total documentos: {stats['total_documents']}")
        print(f"🌿 Raíces indexadas: {stats['indexed_roots']}")
        print(f"📊 Total chunks: {stats['total_chunks']}")
        print(f"🔗 Total conexiones: {stats['total_connections']}")
        print(f"📏 Profundidad promedio: {stats['average_tree_depth']:.1f}")
        print(f"🤖 Dimensión embeddings: {stats['embedding_dimension']}")
        
        # Información de GPU
        if stats.get('gpu_available', False):
            print(f"🚀 Aceleración GPU: ✅ ({stats.get('gpu_count', 0)} GPUs)")
            print(f"⚡ Tipo índice: {stats.get('index_type', 'Unknown')}")
        else:
            print(f"⚠️ GPU: No disponible (usando CPU)")
            print(f"💡 Tip: Instalar CUDA para aceleración GPU")
        
        print(f"⚡ Estado: {'✅ Listo' if stats['is_built'] else '⚠️ Requiere build_index()'}")
        print("=" * 50)
        
        if stats['document_ids']:
            print("� Documentos disponibles:")
            for i, doc_id in enumerate(stats['document_ids'], 1):
                root_chunk = self.root_finder.root_chunks.get(doc_id, 'unknown')
                print(f"   {i}. {doc_id} (raíz: {root_chunk})")
            print()