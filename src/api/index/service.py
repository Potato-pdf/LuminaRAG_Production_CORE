import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import os
from pathlib import Path

from src.parse_docs import parse_documents_with_metadata
from src.config import API_CONFIG, CHUNKING_CONFIG, EMBEDDING_CONFIG
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from .models import IndexResponse
from api.querry_api.models import QueryResponse, ChunkInfo, SystemStats, DocumentInfo, HealthResponse

logger = logging.getLogger(__name__)

load_dotenv()

class IndexService:
    """
    Servicio para indexar documentos desde S3 en colecciones específicas por empresa.
    """

    def __init__(self):
        self.embedding_model = None
        self.node_parser = None
        self._initialized = False

    def initialize(self):
        """Inicializar componentes necesarios para indexación"""
        if self._initialized:
            return

        logger.info("Inicializando servicio de indexación...")

        # Configurar embedding model
        self.embedding_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_CONFIG["model_name"],
            max_length=512,
            device="cpu"
        )

        # Configurar node parser
        self.node_parser = SentenceWindowNodeParser(
            window_size=CHUNKING_CONFIG["chunk_window_size"],
            window_metadata_key="window",
            original_text_metadata_key="original_text"
        )

        self._initialized = True
        logger.info("✅ Servicio de indexación inicializado")

    def index_documents(self, empresa: str, private: bool) -> IndexResponse:
        """
        Indexar documentos de una empresa específica desde S3.

        Args:
            empresa: Nombre de la empresa
            private: Si indexar documentos privados o públicos

        Returns:
            IndexResponse con resultados de la indexación
        """
        if not self._initialized:
            self.initialize()

        start_time = time.time()
        logger.info(f"🏗️ Iniciando indexación para {empresa} ({'privado' if private else 'público'})")

        try:
            # 1. Procesar documentos con metadata desde S3
            api_key = API_CONFIG["llama_cloud_api_key"]
            documents, documents_metadata = parse_documents_with_metadata(api_key=api_key)

            if not documents:
                return IndexResponse(
                    success=False,
                    message=f"No se encontraron documentos para {empresa}",
                    documents_processed=0,
                    chunks_created=0,
                    milvus_collection=f"{empresa}_{'private' if private else 'public'}"
                )

            # 2. Filtrar documentos por empresa y privacidad
            filtered_documents = []
            for doc, metadata in zip(documents, documents_metadata or []):
                if (hasattr(metadata, 'empresa') and metadata.empresa == empresa and
                    hasattr(metadata, 'private') and metadata.private == private):
                    # Agregar metadata al documento de LlamaIndex
                    doc.metadata.update({
                        'empresa': metadata.empresa,
                        'private': metadata.private,
                        's3_key': metadata.s3_key,
                        'file_name': metadata.file_name
                    })
                    filtered_documents.append(doc)

            if not filtered_documents:
                return IndexResponse(
                    success=False,
                    message=f"No se encontraron documentos {'privados' if private else 'públicos'} para {empresa}",
                    documents_processed=0,
                    chunks_created=0,
                    milvus_collection=f"{empresa}_{'private' if private else 'public'}"
                )

            logger.info(f"📄 Procesando {len(filtered_documents)} documentos filtrados")

            # 3. Crear chunks
            nodes = self.node_parser.get_nodes_from_documents(filtered_documents)
            logger.info(f"✅ {len(nodes)} chunks creados")

            # 4. Generar embeddings
            embeddings = []
            for node in nodes:
                embedding = self.embedding_model.get_text_embedding(node.get_content())
                embeddings.append(embedding)

            # 5. Indexar en colección específica
            collection_name = self._index_to_faiss_collection(
                empresa, private, nodes, embeddings
            )

            processing_time = time.time() - start_time

            return IndexResponse(
                success=True,
                message=f"Indexación completada exitosamente para {empresa}",
                documents_processed=len(filtered_documents),
                chunks_created=len(nodes),
                milvus_collection=collection_name
            )

        except Exception as e:
            logger.error(f"Error en indexación: {e}", exc_info=True)
            return IndexResponse(
                success=False,
                message=f"Error en indexación: {str(e)}",
                documents_processed=0,
                chunks_created=0,
                milvus_collection=f"{empresa}_{'private' if private else 'public'}"
            )

    def _index_to_faiss_collection(self, empresa: str, private: bool,
                                  nodes: List, embeddings: List) -> str:
        """
        Indexar chunks en una colección FAISS específica para empresa_privacidad
        """
        import faiss
        import json
        from src.config import STORAGE_CONFIG

        privacidad_str = "private" if private else "public"
        collection_name = f"{empresa}_{privacidad_str}"

        # Crear directorio si no existe
        faiss_dir = Path(STORAGE_CONFIG["base_dir"]) / "faiss_collections"
        faiss_dir.mkdir(parents=True, exist_ok=True)

        faiss_path = faiss_dir / f"{collection_name}.faiss"
        metadata_path = faiss_dir / f"{collection_name}_metadata.json"

        # Preparar datos para FAISS
        dimension = len(embeddings[0]) if embeddings else 768
        faiss_index = faiss.IndexFlatIP(dimension)

        # Convertir embeddings a numpy array
        import numpy as np
        embeddings_array = np.array(embeddings, dtype=np.float32)
        faiss_index.add(embeddings_array)

        # Guardar índice FAISS
        faiss.write_index(faiss_index, str(faiss_path))

        # Preparar y guardar metadata
        metadata = {
            "collection_name": collection_name,
            "empresa": empresa,
            "private": private,
            "document_count": len(set(node.metadata.get('file_name', 'unknown') for node in nodes)),
            "chunk_count": len(nodes),
            "created_at": datetime.now().isoformat(),
            "documents": []
        }

        # Agregar información de documentos
        doc_info = {}
        for i, node in enumerate(nodes):
            file_name = node.metadata.get('file_name', 'unknown')
            if file_name not in doc_info:
                doc_info[file_name] = {
                    "file_name": file_name,
                    "empresa": empresa,
                    "private": private,
                    "chunks": []
                }
            doc_info[file_name]["chunks"].append({
                "id": i,
                "content_preview": node.get_content()[:200] + "..." if len(node.get_content()) > 200 else node.get_content()
            })

        metadata["documents"] = list(doc_info.values())

        # Guardar metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Colección {collection_name} guardada: {faiss_path}")
        return collection_name
    
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
