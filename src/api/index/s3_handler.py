"""
Módulo para manejo de operaciones S3 en el sistema de indexación.
"""
import logging
from pathlib import Path
import boto3

from src.config import S3_FAISS_CONFIG

logger = logging.getLogger(__name__)


class S3Handler:
    """Maneja subidas de índices FAISS a S3"""
    
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
    
    def upload_collection(self, collection_name: str, faiss_path: Path, metadata_path: Path):
        """
        Subir índice FAISS y metadata a S3, luego eliminar archivos locales
        
        Args:
            collection_name: Nombre de la colección
            faiss_path: Ruta local del índice FAISS
            metadata_path: Ruta local de la metadata
            
        Raises:
            RuntimeError: Si falla la subida a S3
        """
        if not self.s3_client:
            raise RuntimeError("Cliente S3 no inicializado")
        
        try:
            bucket = S3_FAISS_CONFIG["bucket_name"]
            s3_prefix = S3_FAISS_CONFIG["prefix"]
            
            # Subir índice FAISS
            s3_faiss_key = f"{s3_prefix}{collection_name}.faiss"
            self.s3_client.upload_file(str(faiss_path), bucket, s3_faiss_key)
            logger.info(f"☁️ Índice FAISS subido a S3: s3://{bucket}/{s3_faiss_key}")
            
            # Subir metadata
            s3_metadata_key = f"{s3_prefix}{collection_name}_metadata.json"
            self.s3_client.upload_file(str(metadata_path), bucket, s3_metadata_key)
            logger.info(f"☁️ Metadata subida a S3: s3://{bucket}/{s3_metadata_key}")
            
            # Eliminar archivos locales después de subir a S3
            faiss_path.unlink(missing_ok=True)
            metadata_path.unlink(missing_ok=True)
            logger.info(f"🗑️ Archivos locales eliminados: {collection_name}")
            
        except Exception as e:
            logger.error(f"Error subiendo a S3: {e}")
            raise RuntimeError(f"No se pudo subir índice a S3: {e}")
