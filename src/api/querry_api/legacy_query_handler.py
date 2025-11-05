"""
Módulo para manejo de consultas legacy (sistema FAISS general).
Mantiene compatibilidad con proceso_query original.
"""
import logging
import time
from typing import Dict, Any, List
from datetime import datetime

from src.FAISS.faiss_integration import load_faiss_system
from src.model_ai.choice_model_llama import connect_ollama
from api.querry_api.models import QueryResponse, ChunkInfo, SystemStats, DocumentInfo, HealthResponse

logger = logging.getLogger(__name__)


class LegacyQueryHandler:
    """Maneja consultas usando el sistema FAISS general (legacy)"""
    
    def __init__(self):
        self.faiss_system = None
        self.llm = None
        self._initialized = False
    
    def initialize(self):
        """Inicializar sistema FAISS general y LLM"""
        if self._initialized:
            return
        
        logger.info("Inicializando LegacyQueryHandler...")
        
        # Cargar sistema FAISS general
        self.faiss_system = load_faiss_system()
        if not self.faiss_system:
            logger.warning("Sistema FAISS general no encontrado")
        
        # Conectar con Ollama
        self.llm = connect_ollama()
        if not self.llm:
            raise RuntimeError("No se pudo conectar con Ollama")
        
        self._initialized = True
        logger.info("✅ LegacyQueryHandler inicializado")
    
    def process_query(self, query: str, k: int = 5, k_roots: int = 5, 
                     include_context: bool = True) -> QueryResponse:
        """Procesar consulta usando sistema FAISS general"""
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")
        
        if self.faiss_system is None:
            raise RuntimeError("Sistema FAISS general no disponible")
        
        start_time = time.time()
        logger.info(f"Procesando consulta legacy: {query[:50]}...")
        
        # Búsqueda FAISS
        search_results = self.faiss_system.search(query, k=k, k_roots=k_roots)
        
        if not search_results:
            return QueryResponse(
                query=query,
                answer="No se encontraron resultados relevantes.",
                chunks=[],
                documents_used=[],
                processing_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
        
        # Preparar contexto
        context = self._prepare_context(search_results, query, include_context)
        
        # Construir prompt
        prompt = self._build_prompt(query, context)
        
        # Generar respuesta
        try:
            response = self.llm.invoke(prompt)
            answer = response if isinstance(response, str) else str(response)
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            answer = f"Error: {str(e)}"
        
        # Construir respuesta
        chunks_info = []
        documents_used = set()
        
        for chunk_id, score, doc_id in search_results:
            chunks_info.append(ChunkInfo(
                chunk_id=str(chunk_id),
                document_id=doc_id,
                content=f"Score: {score}",
                score=score
            ))
            documents_used.add(doc_id)
        
        return QueryResponse(
            query=query,
            answer=answer,
            chunks=chunks_info,
            documents_used=list(documents_used),
            processing_time=time.time() - start_time,
            timestamp=datetime.now().isoformat()
        )
    
    def _prepare_context(self, search_results: List, query: str, 
                        include_context: bool) -> Dict[str, Any]:
        """Preparar contexto enriquecido"""
        return {
            'main_chunks': [],
            'document_sources': set(),
            'hierarchical_info': {},
            'cross_references': []
        }
    
    def _build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Construir prompt para el LLM"""
        return f"CONSULTA: {query}\n\nRESPUESTA:"
    
    def get_stats(self) -> SystemStats:
        """Obtener estadísticas del sistema"""
        if not self._initialized or not self.faiss_system:
            return SystemStats(
                total_documents=0,
                total_chunks=0,
                indexed_roots=0,
                system_status="uninitialized",
                faiss_index_size=0
            )
        
        stats = self.faiss_system.get_stats()
        return SystemStats(
            total_documents=stats.get('total_documents', 0),
            total_chunks=stats.get('total_chunks', 0),
            indexed_roots=stats.get('indexed_roots', 0),
            system_status="operational",
            faiss_index_size=stats.get('indexed_roots', 0)
        )
    
    def get_documents(self) -> List[DocumentInfo]:
        """Obtener lista de documentos disponibles"""
        if not self._initialized or not self.faiss_system:
            return []
        
        stats = self.faiss_system.get_stats()
        documents = []
        
        for doc_id in stats.get('document_ids', []):
            documents.append(DocumentInfo(
                document_id=doc_id,
                root_node="unknown",
                chunk_count=0
            ))
        
        return documents
    
    def health_check(self) -> HealthResponse:
        """Verificar estado del sistema"""
        faiss_loaded = self.faiss_system is not None
        llm_connected = self.llm is not None
        
        status = "healthy" if llm_connected else "unhealthy"
        
        details = {
            "faiss_system": "loaded" if faiss_loaded else "not_loaded",
            "llm": "connected" if llm_connected else "disconnected"
        } if self._initialized else None
        
        return HealthResponse(
            status=status,
            faiss_loaded=faiss_loaded,
            llm_connected=llm_connected,
            details=details
        )
