"""
Módulo para procesamiento de documentos desde S3.
"""
import logging
import boto3
import os
from typing import List, Tuple, Any, Set

from src.parse_docs import parse_documents_with_metadata
from src.config import API_CONFIG, S3_CONFIG, DOCUMENT_SOURCE_CONFIG

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Procesa y filtra documentos desde S3 por empresa y privacidad"""
    
    def __init__(self):
        self.api_key = API_CONFIG["llama_cloud_api_key"]
        self.s3_client = None
        self._initialize_s3_client()
    
    def _initialize_s3_client(self):
        """Inicializar cliente S3 para listar archivos"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=S3_CONFIG["access_key"],
                aws_secret_access_key=S3_CONFIG["secret_key"],
                region_name=S3_CONFIG["region"]
            )
        except Exception as e:
            logger.error(f"Error inicializando cliente S3: {e}")
            self.s3_client = None
    
    def get_document_list(self, empresa: str, private: bool) -> Set[str]:
        """
        Obtener lista de nombres de archivos sin parsear (rápido)
        Busca recursivamente en todas las subcarpetas
        
        Args:
            empresa: Nombre de la empresa
            private: Si listar documentos privados o públicos
            
        Returns:
            Set con nombres de archivos (sin rutas, solo nombres)
        """
        if not self.s3_client:
            return set()
        
        try:
            bucket = DOCUMENT_SOURCE_CONFIG["s3_bucket"]
            privacy_str = "private" if private else "public"
            prefix = f"{empresa}/{privacy_str}/"
            
            logger.info(f"📋 Listando archivos en s3://{bucket}/{prefix}")
            
            paginator = self.s3_client.get_paginator('list_objects_v2')
            file_names = set()
            
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_key = obj['Key']
                        file_name = s3_key.split('/')[-1]
                        
                        # Filtrar:
                        # 1. Carpetas vacías (terminan en /)
                        # 2. Archivos ocultos (empiezan con .)
                        # 3. Solo archivos con extensiones válidas
                        if (file_name and 
                            not file_name.startswith('.') and
                            not s3_key.endswith('/') and
                            file_name.endswith(('.pdf', '.txt', '.docx', '.md', '.doc'))):
                            file_names.add(file_name)
            
            logger.info(f"📄 {len(file_names)} archivos encontrados en {prefix}")
            return file_names
            
        except Exception as e:
            logger.error(f"Error listando archivos S3: {e}")
            return set()
    
    def process_specific_documents(
        self,
        empresa: str,
        private: bool,
        file_names: Set[str]
    ) -> Tuple[List[Any], List[dict]]:
        """
        Procesar solo documentos específicos desde S3 (para indexación incremental)
        Busca archivos recursivamente en todas las subcarpetas
        
        Args:
            empresa: Nombre de la empresa
            private: Si procesar documentos privados o públicos
            file_names: Set de nombres de archivos a procesar
            
        Returns:
            Tupla con (documentos_filtrados, metadatas)
        """
        if not file_names:
            return [], []
        
        logger.info(f"🏗️ Procesando {len(file_names)} documentos específicos para {empresa}")
        
        # Buscar archivos recursivamente en S3
        privacy_str = "private" if private else "public"
        prefix = f"{empresa}/{privacy_str}/"
        local_paths = []
        
        try:
            os.makedirs("/tmp/lumina_s3_downloads", exist_ok=True)
            bucket = DOCUMENT_SOURCE_CONFIG['s3_bucket']
            
            # Listar TODOS los objetos bajo el prefijo
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_key = obj['Key']
                        file_name = s3_key.split('/')[-1]
                        
                        # Solo descargar si está en la lista de archivos solicitados
                        if file_name in file_names:
                            local_path = os.path.join("/tmp/lumina_s3_downloads", file_name)
                            
                            logger.info(f"⬇️ Descargando s3://{bucket}/{s3_key}")
                            self.s3_client.download_file(bucket, s3_key, local_path)
                            local_paths.append(local_path)
                            
        except Exception as e:
            logger.error(f"Error descargando archivos específicos: {e}")
            return [], []
        
        if not local_paths:
            logger.warning(f"No se encontraron archivos para descargar: {file_names}")
            return [], []
        
        # Parsear solo estos archivos
        from llama_parse import LlamaParse
        parser = LlamaParse(api_key=self.api_key, result_type="markdown")
        
        documents = []
        metadatas = []
        
        for local_path in local_paths:
            try:
                parsed_docs = parser.load_data(local_path)
                file_name = os.path.basename(local_path)
                
                for doc in parsed_docs:
                    # Asegurar que metadata existe y tiene file_name
                    if not hasattr(doc, 'metadata') or doc.metadata is None:
                        doc.metadata = {}
                    
                    # Forzar file_name en metadata
                    if isinstance(doc.metadata, dict):
                        doc.metadata['file_name'] = file_name
                        doc.metadata['empresa'] = empresa
                        doc.metadata['private'] = private
                    else:
                        # Si es un objeto, intentar asignar atributos
                        doc.metadata.file_name = file_name
                        doc.metadata.empresa = empresa
                        doc.metadata.private = private
                    
                    documents.append(doc)
                    metadatas.append({
                        'empresa': empresa,
                        'private': private,
                        'file_name': file_name
                    })
            except Exception as e:
                logger.error(f"Error parseando {local_path}: {e}")
        
        logger.info(f"✅ {len(documents)} documentos parseados de {len(file_names)} archivos")
        return documents, metadatas
    
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
            # Manejar tanto diccionarios como objetos DocumentMetadata
            if isinstance(metadata, dict):
                doc_empresa = metadata.get('empresa', '').strip().lower()
                doc_private = metadata.get('private', False)
            else:
                # Es un objeto DocumentMetadata de llama-index
                doc_empresa = getattr(metadata, 'empresa', '').strip().lower() if hasattr(metadata, 'empresa') else ''
                doc_private = getattr(metadata, 'private', False) if hasattr(metadata, 'private') else False
            
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
