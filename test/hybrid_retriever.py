#!/usr/bin/env python3
"""
🔄 RETRIEVER HÍBRIDO INTELIGENTE
===============================

Combina la potencia del grafo con la eficiencia de embeddings vectoriales.
Mejor que RetrieverQueryEngine para casos específicos como el tuyo.
"""

import pickle
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pymilvus import Collection, connections
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

@dataclass
class RetrievalResult:
    """Resultado de retrieval con metadatos completos"""
    chunk_id: str
    content: str
    similarity_score: float
    graph_importance: float
    combined_score: float
    metadata: Dict

class HybridGraphRetriever:
    """
    Retriever híbrido que combina:
    1. Similaridad vectorial (Milvus)
    2. Importancia del grafo (PageRank)
    3. Conectividad contextual
    4. Diversidad de resultados
    """
    
    def __init__(self, 
                 collection_name: str,
                 graph_path: str = 'storage/graphs/document_graph.pkl',
                 embedding_model_name: str = "efederici/e5-base-multilingual-4096"):
        
        self.collection_name = collection_name
        self.collection = Collection(collection_name)
        self.collection.load()
        
        # Cargar grafo
        with open(graph_path, 'rb') as f:
            self.document_graph = pickle.load(f)
        
        # Configurar embedding
        self.embedding_model = HuggingFaceEmbedding(
            model_name=embedding_model_name,
            max_length=512,
            device="cpu"
        )
        
        print(f"🔄 Retriever híbrido inicializado:")
        stats = self.document_graph.get_stats()
        print(f"   📊 Grafo: {stats['nodes']} nodos, {stats['edges']} conexiones")
        print(f"   🗃️ Colección: {self.collection.num_entities} documentos")
    
    def retrieve(self, 
                 query: str, 
                 top_k: int = 10,
                 vector_weight: float = 0.6,
                 graph_weight: float = 0.4,
                 diversity_threshold: float = 0.8) -> List[RetrievalResult]:
        """
        Retrieval híbrido inteligente
        
        Args:
            query: Consulta del usuario
            top_k: Número de resultados
            vector_weight: Peso de similaridad vectorial (0-1)
            graph_weight: Peso de importancia del grafo (0-1)
            diversity_threshold: Umbral para diversidad (0-1)
        """
        
        # 1. BÚSQUEDA VECTORIAL EN MILVUS
        print(f"🔍 Buscando en Milvus con query: '{query[:50]}...'")
        
        # Generar embedding de la consulta
        query_embedding = self.embedding_model.get_text_embedding(query)
        
        # Búsqueda vectorial
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 64}
        }
        
        # Buscar más candidatos para luego filtrar
        vector_results = self.collection.search(
            data=[query_embedding],
            anns_field="vector",
            param=search_params,
            limit=top_k * 3,  # 3x más candidatos
            expr=None,
            output_fields=["text", "metadata"]
        )[0]
        
        print(f"   ✅ {len(vector_results)} candidatos vectoriales")
        
        # 2. ENRIQUECER CON DATOS DEL GRAFO
        enriched_results = []
        
        for hit in vector_results:
            chunk_id = hit.id
            similarity_score = float(hit.score)
            content = hit.entity.get("text", "")
            metadata = hit.entity.get("metadata", {})
            
            # Obtener importancia del grafo
            graph_importance = self.document_graph.get_chunk_importance(chunk_id)
            if graph_importance is None:
                graph_importance = 0.0
            
            # Score combinado
            combined_score = (vector_weight * similarity_score + 
                            graph_weight * graph_importance)
            
            enriched_results.append(RetrievalResult(
                chunk_id=chunk_id,
                content=content,
                similarity_score=similarity_score,
                graph_importance=graph_importance,
                combined_score=combined_score,
                metadata=metadata
            ))
        
        # 3. RANKING HÍBRIDO
        enriched_results.sort(key=lambda x: x.combined_score, reverse=True)
        
        # 4. DIVERSIFICACIÓN INTELIGENTE
        final_results = self._diversify_results(enriched_results, top_k, diversity_threshold)
        
        # 5. EXPANSIÓN CONTEXTUAL DEL GRAFO
        final_results = self._expand_with_graph_context(final_results, max_expansion=2)
        
        print(f"   🎯 {len(final_results)} resultados finales")
        return final_results[:top_k]
    
    def _diversify_results(self, 
                          results: List[RetrievalResult], 
                          top_k: int,
                          threshold: float) -> List[RetrievalResult]:
        """Diversifica resultados para evitar redundancia"""
        
        if len(results) <= top_k:
            return results
        
        diverse_results = [results[0]]  # Siempre incluir el mejor
        
        for candidate in results[1:]:
            if len(diverse_results) >= top_k:
                break
            
            # Verificar diversidad con resultados ya seleccionados
            is_diverse = True
            for selected in diverse_results:
                # Similaridad simple por contenido (puedes mejorar esto)
                content_similarity = self._simple_text_similarity(
                    candidate.content, selected.content
                )
                
                if content_similarity > threshold:
                    is_diverse = False
                    break
            
            if is_diverse:
                diverse_results.append(candidate)
        
        return diverse_results
    
    def _expand_with_graph_context(self, 
                                  results: List[RetrievalResult],
                                  max_expansion: int) -> List[RetrievalResult]:
        """Expande resultados con chunks conectados en el grafo"""
        
        expanded = list(results)
        used_chunks = {r.chunk_id for r in results}
        
        for result in results:
            # Obtener chunks conectados
            connected = self.document_graph.get_connected_chunks(
                result.chunk_id, max_connections=max_expansion
            )
            
            for connected_id, connection_strength in connected:
                if connected_id not in used_chunks and len(expanded) < len(results) * 2:
                    
                    # Obtener contenido del chunk conectado
                    content = self.document_graph.get_chunk_content(connected_id)
                    if content:
                        # Score basado en la conexión
                        expanded_score = result.combined_score * connection_strength * 0.8
                        
                        expanded.append(RetrievalResult(
                            chunk_id=connected_id,
                            content=content,
                            similarity_score=0.0,  # No tiene score vectorial
                            graph_importance=connection_strength,
                            combined_score=expanded_score,
                            metadata={"expanded_from": result.chunk_id}
                        ))
                        
                        used_chunks.add(connected_id)
        
        return expanded
    
    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        """Similaridad simple basada en palabras comunes"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def explain_retrieval(self, query: str, top_k: int = 5) -> None:
        """Explica el proceso de retrieval para debugging"""
        
        print(f"\n🔍 EXPLICACIÓN DEL RETRIEVAL")
        print("="*50)
        print(f"Query: {query}")
        print(f"Top-K: {top_k}")
        
        results = self.retrieve(query, top_k)
        
        for i, result in enumerate(results, 1):
            print(f"\n📄 RESULTADO #{i}")
            print(f"   🆔 ID: {result.chunk_id}")
            print(f"   🎯 Score Vectorial: {result.similarity_score:.4f}")
            print(f"   🕸️ Importancia Grafo: {result.graph_importance:.4f}")
            print(f"   ⚖️ Score Combinado: {result.combined_score:.4f}")
            print(f"   📝 Contenido: {result.content[:100]}...")
            if "expanded_from" in result.metadata:
                print(f"   🔗 Expandido desde: {result.metadata['expanded_from']}")

def test_hybrid_retriever():
    """Test del retriever híbrido"""
    
    from src.config import MILVUS_CONFIG
    
    # Conectar a Milvus
    connections.connect(
        alias="default",
        host=MILVUS_CONFIG["host"],
        port=MILVUS_CONFIG["port"],
        user=MILVUS_CONFIG["user"],
        password=MILVUS_CONFIG["password"]
    )
    
    # Crear retriever
    retriever = HybridGraphRetriever("lumina_manual")
    
    # Test con explicación
    query = "¿Qué es la cobranza administrativa?"
    retriever.explain_retrieval(query, top_k=5)

if __name__ == "__main__":
    test_hybrid_retriever()