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
    
    def index_documents(self, empresa: str, private: bool) -> IndexResponse:
        """
        Indexar documentos de una empresa específica desde S3
        
        Args:
            empresa: Nombre de la empresa
            private: Si indexar documentos privados o públicos
            
        Returns:
            IndexResponse con resultados de la indexación
        """
        if not self._initialized:
            self.initialize()
        
        start_time = time.time()
        
        try:
            # 1. Procesar y filtrar documentos
            filtered_documents, filtered_metadata = self.document_processor.process_documents(
                empresa, private
            )
            
            # 2. Generar chunks y embeddings
            nodes, embeddings = self.embedding_generator.generate_chunks_and_embeddings(
                filtered_documents
            )
            
            # 3. Crear índice FAISS
            collection_name, faiss_path, metadata_path = self.faiss_indexer.create_index(
                empresa, private, nodes, embeddings
            )
            
            # 4. Subir a S3 y eliminar archivos locales
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
