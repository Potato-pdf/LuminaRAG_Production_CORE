import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import json
import faiss
from pathlib import Path

from src.FAISS.faiss_integration import load_faiss_system
from src.model_ai.choice_model_llama import connect_ollama
from src.config import STORAGE_CONFIG, EMBEDDING_CONFIG
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from api.querry_api.models import QueryResponse, ChunkInfo, SystemStats, DocumentInfo, HealthResponse

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
        self.collection_systems = {}  # Cache de sistemas FAISS por colección
        self.embedding_model = None

    def initialize(self):
        """Inicializar el sistema RAG (carga FAISS y conecta LLM)"""
        if self._initialized:
            logger.warning("Sistema ya inicializado")
            return

        logger.info("Inicializando sistema RAG...")

        # 1. Cargar sistema FAISS general
        logger.info("Cargando sistema FAISS...")
        self.faiss_system = load_faiss_system()
        if not self.faiss_system:
            logger.warning("Sistema FAISS general no encontrado - funcionando en modo colección por empresa")
            self.faiss_system = None
        else:
            logger.info("✅ Sistema FAISS cargado")

        # 2. Conectar con Ollama
        logger.info("Conectando con Ollama...")
        self.llm = connect_ollama()
        if not self.llm:
            raise RuntimeError("No se pudo conectar con Ollama")
        logger.info("✅ Ollama conectado")

        # 3. Inicializar modelo de embeddings para consultas específicas
        self.embedding_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_CONFIG["model_name"],
            max_length=512,
            device="cpu"
        )

        self._initialized = True
        logger.info("🎉 Sistema RAG inicializado correctamente")

    def load_collection_system(self, empresa: str, private: bool) -> Optional[Any]:
        """
        Cargar sistema FAISS específico para una colección empresa_privacidad
        """
        privacidad_str = "private" if private else "public"
        collection_name = f"{empresa}_{privacidad_str}"

        # Verificar si ya está en cache
        if collection_name in self.collection_systems:
            return self.collection_systems[collection_name]

        try:
            # Buscar archivo FAISS de la colección
            faiss_dir = Path(STORAGE_CONFIG["base_dir"]) / "faiss_collections"
            faiss_path = faiss_dir / f"{collection_name}.faiss"
            metadata_path = faiss_dir / f"{collection_name}_metadata.json"

            if not faiss_path.exists():
                logger.warning(f"Archivo FAISS no encontrado para colección: {collection_name}")
                return None

            # Cargar índice FAISS
            faiss_index = faiss.read_index(str(faiss_path))

            # Cargar metadata
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

            # Crear sistema simplificado para consultas
            collection_system = {
                'faiss_index': faiss_index,
                'metadata': metadata,
                'collection_name': collection_name,
                'empresa': empresa,
                'private': private
            }

            # Cachear el sistema
            self.collection_systems[collection_name] = collection_system

            logger.info(f"✅ Sistema FAISS cargado para colección: {collection_name}")
            return collection_system

        except Exception as e:
            logger.error(f"Error cargando sistema para colección {collection_name}: {e}")
            return None

    def process_query_by_company(self, query: str, empresa: str, private: bool, k: int = 5) -> QueryResponse:
        """
        Procesar consulta específica para una empresa y tipo de documento (público/privado)
        """
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")

        start_time = time.time()

        logger.info(f"Procesando consulta para {empresa} ({'privado' if private else 'público'}): {query[:50]}...")

        # 1. Cargar sistema específico para la colección
        collection_system = self.load_collection_system(empresa, private)
        if not collection_system:
            return QueryResponse(
                query=query,
                answer=f"No se encontraron documentos {'privados' if private else 'públicos'} para la empresa {empresa}.",
                chunks=[],
                documents_used=[],
                processing_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )

        # 2. Generar embedding de la consulta
        query_embedding = self.embedding_model.get_text_embedding(query)
        if len(query_embedding) != collection_system['faiss_index'].d:
            logger.error(f"Dimensión de embedding incorrecta: {len(query_embedding)} vs {collection_system['faiss_index'].d}")
            return QueryResponse(
                query=query,
                answer="Error en el procesamiento de la consulta.",
                chunks=[],
                documents_used=[],
                processing_time=time.time() - start_time,
                timestamp=datetime.now().isoformat()
            )

        # 3. Buscar en FAISS
        import numpy as np
        query_vector = np.array([query_embedding], dtype=np.float32)
        distances, indices = collection_system['faiss_index'].search(query_vector, k)

        # 4. Preparar resultados
        chunks_info = []
        documents_used = set()
        metadata = collection_system['metadata']

        documents = metadata.get('documents', [])

        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(documents) and idx >= 0:
                doc_info = documents[idx]
                chunks_info.append(ChunkInfo(
                    chunk_id=f"{collection_system['collection_name']}_{idx}",
                    content=f"Documento: {doc_info.get('file_name', 'unknown')} - Empresa: {empresa} ({'Privado' if private else 'Público'})",
                    score=float(1 / (1 + distance)),  # Convertir distancia a similitud
                    document=doc_info.get('file_name', 'unknown')
                ))
                documents_used.add(doc_info.get('file_name', 'unknown'))

        # 5. Generar respuesta con LLM usando contexto limitado
        context = "\n".join([chunk.content for chunk in chunks_info[:3]])  # Usar primeros 3 resultados

        prompt = f"""
        Basándote en los siguientes documentos {'privados' if private else 'públicos'} de la empresa {empresa}:

        {context}

        Responde la siguiente consulta: {query}

        Si no hay información suficiente, indica que no se encontraron datos relevantes.
        """

        try:
            answer = self.llm.invoke(prompt)
            logger.info("✅ Respuesta generada exitosamente")
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            answer = f"Se encontraron {len(chunks_info)} documentos relevantes, pero hubo un error generando la respuesta."

        processing_time = time.time() - start_time

        return QueryResponse(
            query=query,
            answer=answer,
            chunks=chunks_info,
            documents_used=list(documents_used),
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
    
    def process_query(self, query: str, k: int = 5, k_roots: int = 5, 
                    include_context: bool = True) -> QueryResponse:
        """
        Procesar una consulta y retornar respuesta estructurada.
        
        Reutiliza la lógica de FAISSQuerySystem.process_query() sin modificarla.
        """
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")
        
        if self.faiss_system is None:
            return QueryResponse(
                query=query,
                answer="Sistema FAISS general no disponible. Use consultas específicas por empresa.",
                chunks=[],
                documents_used=[],
                processing_time=0.0,
                timestamp=datetime.now().isoformat()
            )
        
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
        
        if self.faiss_system is None:
            return SystemStats(
                total_documents=0,
                total_chunks=0,
                indexed_roots=0,
                system_status="collection_mode",
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
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")
        
        if self.faiss_system is None:
            return []
        
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
        
        status = "healthy" if llm_connected else "unhealthy"
        if faiss_loaded:
            status = "healthy"
        
        details = None
        if self._initialized and faiss_loaded:
            try:
                stats = self.faiss_system.get_stats()
                details = {
                    "documents": stats.get('total_documents', 0),
                    "indexed_roots": stats.get('indexed_roots', 0)
                }
            except:
                pass
        elif self._initialized:
            details = {"mode": "collection_mode"}
        
        return HealthResponse(
            status=status,
            faiss_loaded=faiss_loaded,
            llm_connected=llm_connected,
            details=details
        )
