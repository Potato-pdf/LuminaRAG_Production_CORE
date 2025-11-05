"""
Servicio de indexación refactorizado.
Orquesta los diferentes módulos para indexar documentos.
"""
import logging
import time

from .document_processor import DocumentProcessor
from .embedding_generator import EmbeddingGenerator
from .faiss_indexer import FAISSIndexer
from .s3_handler import S3Handler
from .models import IndexResponse

logger = logging.getLogger(__name__)


class IndexService:
    """
    Servicio principal de indexación.
    Orquesta procesamiento de documentos, generación de embeddings e indexación FAISS.
    """
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.embedding_generator = EmbeddingGenerator()
        self.faiss_indexer = FAISSIndexer()
        self.s3_handler = S3Handler()
        self._initialized = False
    
    def initialize(self):
        """Inicializar componentes del servicio"""
        if self._initialized:
            return
        
        logger.info("Inicializando servicio de indexación...")
        self.embedding_generator.initialize()
        self._initialized = True
        logger.info("✅ Servicio de indexación inicializado")
    
    def index_documents(self, empresa: str, private: bool, force_reindex: bool = False) -> IndexResponse:
        """
        Indexar documentos de una empresa específica desde S3
        
        Args:
            empresa: Nombre de la empresa
            private: Si indexar documentos privados o públicos
            force_reindex: Si True, re-indexa aunque ya exista la colección
            
        Returns:
            IndexResponse con resultados de la indexación
        """
        if not self._initialized:
            self.initialize()
        
        start_time = time.time()
        privacidad_str = "private" if private else "public"
        collection_name = f"{empresa}_{privacidad_str}"
        
        try:
            # 1. Si no es force_reindex, verificar si ya existe y comparar documentos
            if not force_reindex and self.s3_handler.collection_exists(collection_name):
                logger.info(f"🔍 Verificando si hay cambios en {collection_name}...")
                
                # Obtener documentos indexados desde metadata en S3
                indexed_documents = self.s3_handler.get_indexed_documents(collection_name)
                
                if indexed_documents is not None:
                    # Obtener lista de documentos actuales SIN parsear (rápido)
                    current_documents = self.document_processor.get_document_list(empresa, private)
                    
                    # Comparar documentos
                    new_documents = current_documents - indexed_documents
                    removed_documents = indexed_documents - current_documents
                    
                    if not new_documents and not removed_documents:
                        logger.info(f"⏭️ No hay cambios en {collection_name}. Omitiendo re-indexación.")
                        return IndexResponse(
                            success=True,
                            message=f"Sin cambios en {collection_name}. Documentos: {len(indexed_documents)}. Use force_reindex=true para re-indexar.",
                            documents_processed=0,
                            chunks_created=0,
                            milvus_collection=collection_name,
                            processing_time=time.time() - start_time
                        )
                    else:
                        if new_documents:
                            logger.info(f"📄 {len(new_documents)} nuevos documentos detectados: {new_documents}")
                        if removed_documents:
                            logger.info(f"🗑️ {len(removed_documents)} documentos eliminados: {removed_documents}")
                        
                        # INDEXACIÓN INCREMENTAL: Solo procesar documentos nuevos
                        if new_documents and not removed_documents:
                            logger.info(f"🔄 Indexación incremental en {collection_name}")
                            filtered_documents, filtered_metadata = self.document_processor.process_specific_documents(
                                empresa, private, new_documents
                            )
                            is_incremental = True
                        else:
                            # Si hay documentos eliminados, re-indexar todo
                            logger.warning(f"⚠️ Documentos eliminados detectados. Re-indexando toda la colección.")
                            filtered_documents, filtered_metadata = self.document_processor.process_documents(
                                empresa, private
                            )
                            is_incremental = False
                        
                        # Procesar solo si hay documentos
                        if not filtered_documents:
                            logger.info(f"⏭️ No hay documentos para indexar.")
                            return IndexResponse(
                                success=True,
                                message=f"No hay documentos nuevos en {collection_name}",
                                documents_processed=0,
                                chunks_created=0,
                                milvus_collection=collection_name,
                                processing_time=time.time() - start_time
                            )
            else:
                # Primera indexación o force_reindex
                logger.info(f"🆕 Primera indexación de {collection_name}")
                filtered_documents, filtered_metadata = self.document_processor.process_documents(
                    empresa, private
                )
                is_incremental = False
            
            # 2. Si llegamos aquí sin filtered_documents, procesarlos
            if 'filtered_documents' not in locals():
                filtered_documents, filtered_metadata = self.document_processor.process_documents(
                    empresa, private
                )
                is_incremental = False
            
            # 3. Generar chunks y embeddings
            nodes, embeddings = self.embedding_generator.generate_chunks_and_embeddings(
                filtered_documents
            )
            
            # 4. Si es incremental, descargar índice existente de S3
            if is_incremental:
                logger.info(f"⬇️ Descargando índice existente de S3 para actualización incremental")
                self.s3_handler.download_collection(collection_name)
            
            # 5. Crear o actualizar índice FAISS (con soporte incremental)
            collection_name, faiss_path, metadata_path = self.faiss_indexer.create_index(
                empresa, private, nodes, embeddings, incremental=is_incremental
            )
            
            # 6. Subir a S3 y eliminar archivos locales
            self.s3_handler.upload_collection(collection_name, faiss_path, metadata_path)
            
            processing_time = time.time() - start_time
            
            return IndexResponse(
                success=True,
                message=f"Indexación completada exitosamente para {empresa}",
                documents_processed=len(filtered_documents),
                chunks_created=len(nodes),
                milvus_collection=collection_name,
                processing_time=processing_time
            )
        
        except Exception as e:
            logger.error(f"Error en indexación: {e}", exc_info=True)
            return IndexResponse(
                success=False,
                message=f"Error en indexación: {str(e)}",
                documents_processed=0,
                chunks_created=0,
                milvus_collection=f"{empresa}_{'private' if private else 'public'}",
                processing_time=time.time() - start_time
            )
