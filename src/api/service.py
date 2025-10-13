"""
🔧 SERVICIO DE CONSULTAS PARA LA API
====================================

Capa de servicio que encapsula la lógica del sistema RAG
sin modificar la implementación existente.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.FAISS.faiss_integration import load_faiss_system
from src.model_ai.choice_model_llama import connect_ollama
from src.api.models import QueryResponse, ChunkInfo, SystemStats, DocumentInfo, HealthResponse

logger = logging.getLogger(__name__)


class QueryService:
    """
    Servicio que encapsula el sistema de consultas RAG.
    Reutiliza toda la lógica existente sin modificaciones.
    """
    
    def __init__(self):
        self.faiss_system = None
        self.llm = None
        self._initialized = False
    
    def initialize(self):
        """Inicializar el sistema RAG (carga FAISS y conecta LLM)"""
        if self._initialized:
            logger.warning("Sistema ya inicializado")
            return
        
        logger.info("Inicializando sistema RAG...")
        
        # 1. Cargar sistema FAISS
        logger.info("Cargando sistema FAISS...")
        self.faiss_system = load_faiss_system()
        if not self.faiss_system:
            raise RuntimeError("No se pudo cargar el sistema FAISS")
        logger.info("✅ Sistema FAISS cargado")
        
        # 2. Conectar con Ollama
        logger.info("Conectando con Ollama...")
        self.llm = connect_ollama()
        if not self.llm:
            raise RuntimeError("No se pudo conectar con Ollama")
        logger.info("✅ Ollama conectado")
        
        self._initialized = True
        logger.info("🎉 Sistema RAG inicializado correctamente")
    
    def process_query(self, query: str, k: int = 5, k_roots: int = 5, 
                     include_context: bool = True) -> QueryResponse:
        """
        Procesar una consulta y retornar respuesta estructurada.
        
        Reutiliza la lógica de FAISSQuerySystem.process_query() sin modificarla.
        """
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")
        
        start_time = time.time()
        
        logger.info(f"Procesando consulta: {query[:50]}...")
        
        # 1. Búsqueda FAISS + Árboles (lógica existente)
        search_results = self.faiss_system.search(query, k=k, k_roots=k_roots)
        
        if not search_results:
            logger.warning("No se encontraron resultados")
            return QueryResponse(
                query=query,
                answer="No se encontraron resultados relevantes para tu consulta.",
                chunks=[],
                documents_used=[],
                processing_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )
        
        # 2. Preparar contexto (lógica existente)
        context = self._prepare_context(search_results, query, include_context)
        
        # 3. Construir prompt (lógica existente)
        prompt = self._build_prompt(query, context)
        
        # 4. Generar respuesta con LLM
        try:
            answer = self.llm.invoke(prompt)
            logger.info("✅ Respuesta generada exitosamente")
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            answer = f"Error generando respuesta. Se encontraron {len(search_results)} chunks relevantes."
        
        # 5. Construir respuesta estructurada
        chunks_info = []
        documents_used = set()
        
        for chunk_id, score, doc_id in search_results:
            # Obtener contenido del chunk
            chunk_content = None
            for doc_name, hierarchical_graph in self.faiss_system.root_finder.document_trees.items():
                if hierarchical_graph.chunk_exists(chunk_id):
                    chunk_content = hierarchical_graph.get_chunk_content(chunk_id)
                    break
            
            if chunk_content:
                chunks_info.append(ChunkInfo(
                    chunk_id=chunk_id,
                    content=chunk_content[:500] + "..." if len(chunk_content) > 500 else chunk_content,
                    score=float(score),
                    document=doc_id
                ))
                documents_used.add(doc_id)
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=query,
            answer=answer,
            chunks=chunks_info,
            documents_used=list(documents_used),
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
    
    def _prepare_context(self, search_results: List, query: str, 
                        include_context: bool) -> Dict[str, Any]:
        """
        Preparar contexto enriquecido (lógica copiada de FAISSQuerySystem).
        """
        context = {
            'main_chunks': [],
            'document_sources': set(),
            'hierarchical_info': {},
            'cross_references': []
        }
        
        # Procesar resultados principales
        for chunk_id, score, doc_id in search_results:
            chunk_content = None
            
            # Obtener contenido del chunk
            for doc_name, hierarchical_graph in self.faiss_system.root_finder.document_trees.items():
                if hierarchical_graph.chunk_exists(chunk_id):
                    chunk_content = hierarchical_graph.get_chunk_content(chunk_id)
                    break
            
            if chunk_content:
                context['main_chunks'].append({
                    'id': chunk_id,
                    'content': chunk_content,
                    'score': score,
                    'document': doc_id
                })
                context['document_sources'].add(doc_id)
        
        # Contexto adicional si está habilitado
        if include_context and search_results:
            first_chunk_id = search_results[0][0]
            
            # Contexto dentro del documento
            doc_context = self.faiss_system.get_document_context(first_chunk_id, context_size=2)
            
            # Contexto entre documentos
            cross_context = self.faiss_system.get_cross_document_context(first_chunk_id, query, max_docs=2)
            
            # Agregar contenido de contextos
            for chunk_id in doc_context + cross_context:
                for doc_name, hierarchical_graph in self.faiss_system.root_finder.document_trees.items():
                    if hierarchical_graph.chunk_exists(chunk_id):
                        content = hierarchical_graph.get_chunk_content(chunk_id)
                        if content:
                            context['cross_references'].append({
                                'id': chunk_id,
                                'content': content,
                                'document': doc_name
                            })
                        break
        
        return context
    
    def _build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """
        Construir prompt para el LLM (lógica copiada de FAISSQuerySystem).
        """
        prompt_parts = [
            "Eres un asistente experto que responde preguntas basándose en documentos técnicos.",
            f"CONSULTA: {query}",
            "",
            "INFORMACIÓN RELEVANTE:"
        ]
        
        # Agregar chunks principales
        for i, chunk in enumerate(context['main_chunks'], 1):
            prompt_parts.extend([
                f"[FRAGMENTO {i}] (Score: {chunk['score']:.3f}, Documento: {chunk['document']})",
                chunk['content'],
                ""
            ])
        
        # Agregar contexto adicional si existe
        if context['cross_references']:
            prompt_parts.append("CONTEXTO ADICIONAL:")
            for i, ref in enumerate(context['cross_references'][:3], 1):
                prompt_parts.extend([
                    f"[CONTEXTO {i}] (Documento: {ref['document']})",
                    ref['content'][:300] + "..." if len(ref['content']) > 300 else ref['content'],
                    ""
                ])
        
        # Instrucciones finales
        prompt_parts.extend([
            "INSTRUCCIONES:",
            "1. Responde la consulta basándote únicamente en la información proporcionada",
            "2. Si la información no es suficiente, indícalo claramente",
            "3. Menciona las fuentes (documentos) cuando sea relevante",
            "4. Sé conciso pero completo",
            "",
            "RESPUESTA:"
        ])
        
        return "\n".join(prompt_parts)
    
    def get_stats(self) -> SystemStats:
        """Obtener estadísticas del sistema"""
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")
        
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
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")
        
        stats = self.faiss_system.get_stats()
        documents = []
        
        for doc_id in stats.get('document_ids', []):
            root_chunk = self.faiss_system.root_finder.root_chunks.get(doc_id, 'unknown')
            
            # Obtener estadísticas del documento
            chunk_count = 0
            if doc_id in self.faiss_system.root_finder.document_trees:
                hierarchical_graph = self.faiss_system.root_finder.document_trees[doc_id]
                doc_stats = hierarchical_graph.get_hierarchical_stats()
                chunk_count = doc_stats.get('total_chunks', 0)
            
            documents.append(DocumentInfo(
                document_id=doc_id,
                root_chunk_id=root_chunk,
                total_chunks=chunk_count
            ))
        
        return documents
    
    def health_check(self) -> HealthResponse:
        """Verificar estado del sistema"""
        faiss_loaded = self.faiss_system is not None
        llm_connected = self.llm is not None
        
        status = "healthy" if (faiss_loaded and llm_connected) else "unhealthy"
        
        details = None
        if self._initialized:
            try:
                stats = self.faiss_system.get_stats()
                details = {
                    "documents": stats.get('total_documents', 0),
                    "indexed_roots": stats.get('indexed_roots', 0)
                }
            except:
                pass
        
        return HealthResponse(
            status=status,
            faiss_loaded=faiss_loaded,
            llm_connected=llm_connected,
            details=details
        )
