"""
Módulo para procesamiento de documentos desde S3.
"""
import logging
from typing import List, Tuple, Any

from src.parse_docs import parse_documents_with_metadata
from src.config import API_CONFIG

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Procesa y filtra documentos desde S3 por empresa y privacidad"""
    
    def __init__(self):
        self.api_key = API_CONFIG["llama_cloud_api_key"]
    
    def process_documents(
        self, 
        empresa: str, 
        private: bool
    ) -> Tuple[List[Any], List[dict]]:
        """
        Procesar y filtrar documentos desde S3
        
        Args:
            empresa: Nombre de la empresa
            private: Si procesar documentos privados o públicos
            
        Returns:
            Tupla con (documentos_filtrados, metadatas)
            
        Raises:
            ValueError: Si no se encuentran documentos o están vacíos
        """
        logger.info(f"🏗️ Procesando documentos para {empresa} ({'privado' if private else 'público'})")
        
        # 1. Procesar documentos con metadata desde S3
        documents, documents_metadata = parse_documents_with_metadata(api_key=self.api_key)
        
        if not documents:
            raise ValueError("No se encontraron documentos para procesar")
        
        # 2. Filtrar documentos por empresa y privacidad
        filtered_documents = []
        filtered_metadata = []
        
        for doc, metadata in zip(documents, documents_metadata or []):
            doc_empresa = metadata.get('empresa', '').strip().lower()
            doc_private = metadata.get('private', False)
            
            if doc_empresa == empresa.strip().lower() and doc_private == private:
                filtered_documents.append(doc)
                filtered_metadata.append(metadata)
        
        if not filtered_documents:
            raise ValueError(
                f"No se encontraron documentos para {empresa} "
                f"({'privados' if private else 'públicos'})"
            )
        
        logger.info(f"📄 {len(filtered_documents)} documentos filtrados de {len(documents)} totales")
        
        return filtered_documents, filtered_metadata
