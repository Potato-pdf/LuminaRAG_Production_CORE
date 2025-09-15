import faiss
import numpy as np
from typing import Dict, List, Tuple, Optional

class RootFinder:
    """
    🌿 BUSCADOR DE RAÍCES CON FAISS
    ===============================
    
    Encuentra las raíces de documentos más relevantes usando FAISS
    para luego buscar específicamente en esos árboles.
    """
    
    def __init__(self, embedding_model=None):
        self.document_trees = {}  # {doc_id: hierarchical_graph}
        self.doc_ids = []  # Orden de documentos
        self.root_embeddings = []  # Embeddings de raíces
        self.root_chunks = {}  # {doc_id: root_chunk_id}
        self.index = None
        
        # Configurar modelo de embedding
        if embedding_model:
            self.embedding_model = embedding_model
        else:
            try:
                from ..embedding.multilingual.choice_embedding import choice_embedding
                self.embedding_model = choice_embedding()
            except ImportError:
                print("⚠️ No se pudo cargar choice_embedding, usar modelo manual")
                self.embedding_model = None
        
    def add_document(self, doc_id: str, hierarchical_graph, root_chunk_id: str):
        """
        Agregar documento con su árbol jerárquico
        
        Args:
            doc_id: ID del documento
            hierarchical_graph: Grafo jerárquico del documento
            root_chunk_id: ID del chunk raíz
        """
        # Obtener contenido de la raíz para generar embedding
        root_content = hierarchical_graph.get_chunk_content(root_chunk_id)
        if not root_content:
            print(f"⚠️ No se pudo obtener contenido de raíz para {doc_id}")
            return
            
        # Generar embedding de la raíz
        root_embedding = self._get_text_embedding(root_content)
        
        # Almacenar información
        self.document_trees[doc_id] = hierarchical_graph
        self.doc_ids.append(doc_id)
        self.root_embeddings.append(root_embedding)
        self.root_chunks[doc_id] = root_chunk_id
        
        print(f"📄 Documento agregado: {doc_id} (raíz: {root_chunk_id})")

    def _get_text_embedding(self, text: str) -> np.ndarray:
        """Obtener embedding de texto"""
        try:
            if hasattr(self.embedding_model, 'get_text_embedding'):
                return np.array(self.embedding_model.get_text_embedding(text))
            elif hasattr(self.embedding_model, 'encode'):
                return self.embedding_model.encode([text])[0]
            else:
                # Fallback: usar método directo
                return np.array(self.embedding_model(text))
        except Exception as e:
            print(f"❌ Error generando embedding: {e}")
            # Retornar vector cero como fallback
            return np.zeros(768, dtype=np.float32)

    def build_index(self):
        """Construir índice FAISS-GPU con embeddings de raíces"""
        if not self.root_embeddings:
            print("❌ No hay embeddings de raíces para indexar")
            return False
            
        try:
            # Convertir a array numpy
            embeddings_array = np.array(self.root_embeddings, dtype=np.float32)
            dimension = embeddings_array.shape[1]
            
            # Verificar disponibilidad de GPU
            gpu_available = faiss.get_num_gpus() > 0
            
            if gpu_available:
                print(f"🚀 Construyendo índice FAISS-GPU (GPUs disponibles: {faiss.get_num_gpus()})")
                
                # Crear índice optimizado para GPU
                if len(self.root_embeddings) < 1000:
                    # Para conjuntos pequeños: IndexFlatIP en GPU
                    cpu_index = faiss.IndexFlatIP(dimension)
                    self.index = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), 0, cpu_index)
                else:
                    # Para conjuntos grandes: IndexIVFFlat en GPU
                    quantizer = faiss.IndexFlatIP(dimension)
                    cpu_index = faiss.IndexIVFFlat(quantizer, dimension, min(256, len(self.root_embeddings)//4))
                    self.index = faiss.index_cpu_to_gpu(faiss.StandardGpuResources(), 0, cpu_index)
                    
                    # Entrenar el índice IVF
                    faiss.normalize_L2(embeddings_array)
                    self.index.train(embeddings_array)
            else:
                print("⚠️ GPU no disponible, usando CPU (considera instalar CUDA)")
                # Fallback a CPU con índice optimizado
                self.index = faiss.IndexFlatIP(dimension)
            
            # Normalizar embeddings para cosine similarity
            faiss.normalize_L2(embeddings_array)
            
            # Agregar al índice
            self.index.add(embeddings_array)
            
            gpu_status = "GPU" if gpu_available else "CPU"
            print(f"✅ Índice FAISS-{gpu_status} construido: {self.index.ntotal} raíces, dim={dimension}")
            return True
            
        except Exception as e:
            print(f"❌ Error construyendo índice FAISS: {e}")
            print("💡 Tip: Para GPU, verificar instalación de CUDA y PyTorch")
            return False

    def find_relevant_roots(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Encontrar las k raíces más relevantes para la query
        
        Returns:
            Lista de (doc_id, similarity_score)
        """
        if not self.index:
            print("❌ Índice FAISS no construido")
            return []
            
        try:
            # Generar embedding de la query
            query_embedding = self._get_text_embedding(query)
            query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
            
            # Normalizar para cosine similarity
            faiss.normalize_L2(query_embedding)
            
            # Buscar en FAISS
            scores, indices = self.index.search(query_embedding, min(k, len(self.doc_ids)))
            
            # Mapear resultados a doc_ids
            relevant_roots = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.doc_ids) and idx >= 0:  # Solo filtrar índices inválidos
                    doc_id = self.doc_ids[idx]
                    relevant_roots.append((doc_id, float(score)))
            
            print(f"🔍 Raíces encontradas: {len(relevant_roots)}")
            for doc_id, score in relevant_roots:
                print(f"   📄 {doc_id}: {score:.4f}")
                
            return relevant_roots
            
        except Exception as e:
            print(f"❌ Error en búsqueda FAISS: {e}")
            return []

    def search_in_trees(self, query: str, relevant_roots: List[Tuple[str, float]], k_per_tree: int = 3) -> List[Tuple[str, float, str]]:
        """
        Buscar en los árboles específicos de las raíces relevantes
        
        Returns:
            Lista de (chunk_id, combined_score, doc_id)
        """
        all_results = []
        
        for doc_id, root_score in relevant_roots:
            if doc_id not in self.document_trees:
                continue
                
            hierarchical_graph = self.document_trees[doc_id]
            
            try:
                # Buscar en el grafo jerárquico específico
                tree_results = hierarchical_graph.get_most_important_chunks_hierarchical(
                    top_k=k_per_tree, 
                    strategy="mixed"
                )
                
                # Combinar scores: root_score (FAISS) + tree_score (PageRank)
                for chunk_id, tree_score, chunk_doc in tree_results:
                    # Score combinado: 70% FAISS root score + 30% tree PageRank
                    combined_score = root_score * 0.7 + tree_score * 0.3
                    all_results.append((chunk_id, combined_score, doc_id))
                    
            except Exception as e:
                print(f"⚠️ Error buscando en árbol {doc_id}: {e}")
                continue
        
        # Ordenar por score combinado
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results

    def search(self, query: str, k: int = 5, k_roots: int = 5) -> List[Tuple[str, float, str]]:
        """
        Búsqueda completa: FAISS + árboles específicos
        
        Args:
            query: Consulta de texto
            k: Número total de resultados finales
            k_roots: Número de raíces a considerar
            
        Returns:
            Lista de (chunk_id, score, doc_id)
        """
        print(f"\n🔍 BÚSQUEDA FAISS + ÁRBOLES JERÁRQUICOS")
        print(f"Query: {query[:100]}...")
        print("-" * 50)
        
        # 1. Encontrar raíces relevantes con FAISS
        relevant_roots = self.find_relevant_roots(query, k_roots)
        if not relevant_roots:
            print("❌ No se encontraron raíces relevantes")
            return []
        
        # 2. Buscar en los árboles específicos
        k_per_tree = max(2, k // len(relevant_roots))  # Distribuir búsquedas
        results = self.search_in_trees(query, relevant_roots, k_per_tree)
        
        # 3. Retornar top-k resultados finales
        final_results = results[:k]
        
        print(f"\n📊 RESULTADOS FINALES: {len(final_results)}")
        for i, (chunk_id, score, doc_id) in enumerate(final_results, 1):
            print(f"   {i}. {chunk_id} (doc: {doc_id}) - score: {score:.4f}")
        
        return final_results

    def get_stats(self) -> Dict:
        """Obtener estadísticas del sistema FAISS"""
        return {
            'total_documents': len(self.document_trees),
            'indexed_roots': self.index.ntotal if self.index else 0,
            'embedding_dimension': len(self.root_embeddings[0]) if self.root_embeddings else 0,
            'document_ids': self.doc_ids.copy()
        }    