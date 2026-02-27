"""
Módulo para manejo de operaciones S3 en el sistema de consultas.
"""
import logging
from pathlib import Path
import boto3

from src.config import S3_FAISS_CONFIG

logger = logging.getLogger(__name__)


class S3Handler:
    """Maneja descargas de índices FAISS desde S3"""
    
    def __init__(self):
        self.s3_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializar cliente S3"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=S3_FAISS_CONFIG["access_key"],
                aws_secret_access_key=S3_FAISS_CONFIG["secret_key"],
                region_name=S3_FAISS_CONFIG["region"]
            )
        except Exception as e:
            logger.error(f"Error inicializando cliente S3: {e}")
            self.s3_client = None
    
    def download_collection(self, collection_name: str, faiss_path: Path, metadata_path: Path) -> bool:
        """
        Descargar índice FAISS y metadata desde S3
        
        Args:
            collection_name: Nombre de la colección
            faiss_path: Ruta local para guardar el índice FAISS
            metadata_path: Ruta local para guardar la metadata
            
        Returns:
            True si la descarga fue exitosa, False en caso contrario
        """
        if not self.s3_client:
            logger.error("Cliente S3 no inicializado")
            return False
            
        try:
            bucket = S3_FAISS_CONFIG["bucket_name"]
            s3_prefix = S3_FAISS_CONFIG["prefix"]
            
            # Asegurar que el directorio local existe
            faiss_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Descargar índice FAISS
            s3_faiss_key = f"{s3_prefix}{collection_name}.faiss"
            self.s3_client.download_file(bucket, s3_faiss_key, str(faiss_path))
            logger.info(f"☁️ Índice FAISS descargado desde S3: {s3_faiss_key}")
            
            # Descargar metadata
            s3_metadata_key = f"{s3_prefix}{collection_name}_metadata.json"
            self.s3_client.download_file(bucket, s3_metadata_key, str(metadata_path))
            logger.info(f"☁️ Metadata descargada desde S3: {s3_metadata_key}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error descargando desde S3: {e}")
            return False
