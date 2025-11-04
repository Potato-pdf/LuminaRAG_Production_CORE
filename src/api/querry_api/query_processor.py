"""
Módulo para procesamiento de consultas RAG.
"""
import logging
import time
import numpy as np
from typing import List, Dict, Any
from datetime import datetime

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from src.config import EMBEDDING_CONFIG
from src.model_ai.choice_model_llama import connect_ollama
from api.querry_api.models import QueryResponse, ChunkInfo

logger = logging.getLogger(__name__)


class QueryProcessor:
    """Procesa consultas contra colecciones FAISS usando LLM"""
    
    def __init__(self):
        self.embedding_model = None
        self.llm = None
        self._initialized = False
    
    def initialize(self):
        """Inicializar modelo de embeddings y LLM"""
        if self._initialized:
            return
        
        logger.info("Inicializando QueryProcessor...")
        
        # Inicializar modelo de embeddings
        self.embedding_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_CONFIG["model_name"],
            max_length=512,
            device="cpu"
        )
        
        # Conectar con Ollama
        self.llm = connect_ollama()
        if not self.llm:
            raise RuntimeError("No se pudo conectar con Ollama")
        
        self._initialized = True
        logger.info("✅ QueryProcessor inicializado")
    
    def process_query(
        self, 
        query: str, 
        collection_system: Dict[str, Any], 
        k: int = 5
    ) -> QueryResponse:
        """
        Procesar consulta contra una colección específica
        
        Args:
            query: Texto de la consulta
            collection_system: Sistema de colección con índice FAISS y metadata
            k: Número de chunks a recuperar
            
        Returns:
            QueryResponse con la respuesta generada
        """
        if not self._initialized:
            raise RuntimeError("QueryProcessor no inicializado")
        
        start_time = time.time()
        
        empresa = collection_system['empresa']
        private = collection_system['private']
        
        logger.info(f"Procesando consulta para {empresa} ({'privado' if private else 'público'}): {query[:50]}...")
        
        # 1. Generar embedding de la consulta
        query_embedding = self.embedding_model.get_text_embedding(query)
        if len(query_embedding) != collection_system['faiss_index'].d:
            raise ValueError(
                f"Dimensión del embedding ({len(query_embedding)}) no coincide "
                f"con índice FAISS ({collection_system['faiss_index'].d})"
            )
        
        # 2. Buscar en FAISS
        query_vector = np.array([query_embedding], dtype=np.float32)
        distances, indices = collection_system['faiss_index'].search(query_vector, k)
        
        # 3. Preparar resultados con contenido real de los chunks
        chunks_info = self._prepare_chunks(
            distances[0], 
            indices[0], 
            collection_system['metadata']
        )
        
        # 4. Generar respuesta con LLM
        if not chunks_info:
            return QueryResponse(
                query=query,
                answer=f"No se encontraron documentos {'privados' if private else 'públicos'} relevantes para {empresa}.",
                chunks=[],
                documents_used=[],
                processing_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
        
        answer = self._generate_answer(query, chunks_info, empresa, private)
        
        # 5. Extraer documentos usados
        documents_used = list(set(chunk.document_id for chunk in chunks_info))
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=query,
            answer=answer,
            chunks=chunks_info,
            documents_used=documents_used,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
    
    def _prepare_chunks(
        self, 
        distances: np.ndarray, 
        indices: np.ndarray, 
        metadata: Dict[str, Any]
    ) -> List[ChunkInfo]:
        """Preparar información de chunks desde resultados de búsqueda"""
        chunks_info = []
        chunks_data = metadata.get('chunks', [])
        
        for distance, idx in zip(distances, indices):
            if idx < 0 or idx >= len(chunks_data):
                continue
            
            chunk_data = chunks_data[idx]
            chunks_info.append(ChunkInfo(
                chunk_id=str(chunk_data.get('id', idx)),
                document_id=chunk_data.get('file_name', 'unknown'),
                content=chunk_data.get('content', ''),
                score=float(distance)
            ))
        
        return chunks_info
    
    def _generate_answer(
        self, 
        query: str, 
        chunks_info: List[ChunkInfo], 
        empresa: str, 
        private: bool
    ) -> str:
        """Generar respuesta usando LLM"""
        # Construir contexto con los chunks más relevantes
        context_parts = []
        for i, chunk in enumerate(chunks_info[:5], 1):
            context_parts.append(f"Fragmento {i} (de {chunk.document_id}):\n{chunk.content}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""
Eres un asistente especializado en información de la empresa {empresa}. 
Solo tienes acceso a documentos {'PRIVADOS' if private else 'PÚBLICOS'} de esta empresa.

RESTRICCIONES IMPORTANTES: 
- Responde ÚNICAMENTE basándote en la información de los fragmentos de documentos {'privados' if private else 'públicos'} de {empresa} proporcionados abajo.
- NO uses conocimiento general ni información de otras fuentes.
- Si la consulta requiere información que no está en estos fragmentos, indica claramente que no tienes acceso a esa información en los documentos {'privados' if private else 'públicos'} disponibles.
- Cita el número del fragmento cuando uses información de él (ej: "Según el Fragmento 1...").

FRAGMENTOS DE DOCUMENTOS {'PRIVADOS' if private else 'PÚBLICOS'} DE {empresa}:
{context}

CONSULTA: {query}

Respuesta (solo basada en los fragmentos anteriores):"""
        
        try:
            return self.llm.complete(prompt).text
        except Exception as e:
            logger.error(f"Error generando respuesta con LLM: {e}")
            return f"Error al generar respuesta: {str(e)}"
