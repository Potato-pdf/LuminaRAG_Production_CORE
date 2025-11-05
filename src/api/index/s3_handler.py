"""
Módulo para manejo de operaciones S3 en el sistema de indexación.
"""
import logging
import json
from pathlib import Path
from typing import Optional, Set
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
    
    def collection_exists(self, collection_name: str) -> bool:
        """
        Verificar si una colección ya existe en S3
        
        Args:
            collection_name: Nombre de la colección a verificar
            
        Returns:
            True si la colección existe en S3, False en caso contrario
        """
        if not self.s3_client:
            return False
        
        try:
            bucket = S3_FAISS_CONFIG["bucket_name"]
            s3_prefix = S3_FAISS_CONFIG["prefix"]
            s3_faiss_key = f"{s3_prefix}{collection_name}.faiss"
            
            # Verificar si existe el archivo .faiss
            self.s3_client.head_object(Bucket=bucket, Key=s3_faiss_key)
            return True
        except:
            return False
    
    def get_indexed_documents(self, collection_name: str) -> Optional[Set[str]]:
        """
        Obtener lista de documentos ya indexados en una colección
        
        Args:
            collection_name: Nombre de la colección
            
        Returns:
            Set con nombres de archivos indexados, o None si no existe la colección
        """
        if not self.s3_client:
            return None
        
        try:
            bucket = S3_FAISS_CONFIG["bucket_name"]
            s3_prefix = S3_FAISS_CONFIG["prefix"]
            s3_metadata_key = f"{s3_prefix}{collection_name}_metadata.json"
            
            # Descargar metadata
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
                self.s3_client.download_file(bucket, s3_metadata_key, tmp.name)
                tmp.seek(0)
                with open(tmp.name, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Extraer nombres de documentos únicos
                documents = metadata.get('documents', [])
                file_names = {doc['file_name'] for doc in documents if 'file_name' in doc}
                
                # Filtrar 'unknown' que son errores de metadata anterior
                file_names.discard('unknown')
                
                return file_names
        except Exception as e:
            logger.warning(f"No se pudo obtener lista de documentos indexados: {e}")
            return None
    
    def download_collection(self, collection_name: str) -> bool:
        """
        Descargar índice FAISS y metadata desde S3 para actualización incremental
        
        Args:
            collection_name: Nombre de la colección a descargar
            
        Returns:
            True si la descarga fue exitosa, False en caso contrario
        """
        if not self.s3_client:
            logger.error("Cliente S3 no inicializado")
            return False
        
        try:
            bucket = S3_FAISS_CONFIG["bucket_name"]
            s3_prefix = S3_FAISS_CONFIG["prefix"]
            
            # Crear directorio local si no existe
            from src.config import STORAGE_CONFIG
            local_dir = Path(STORAGE_CONFIG["base_dir"]) / "faiss_collections"
            local_dir.mkdir(parents=True, exist_ok=True)
            
            # Descargar índice FAISS
            s3_faiss_key = f"{s3_prefix}{collection_name}.faiss"
            local_faiss_path = local_dir / f"{collection_name}.faiss"
            self.s3_client.download_file(bucket, s3_faiss_key, str(local_faiss_path))
            logger.info(f"⬇️ Índice FAISS descargado: {local_faiss_path}")
            
            # Descargar metadata
            s3_metadata_key = f"{s3_prefix}{collection_name}_metadata.json"
            local_metadata_path = local_dir / f"{collection_name}_metadata.json"
            self.s3_client.download_file(bucket, s3_metadata_key, str(local_metadata_path))
            logger.info(f"⬇️ Metadata descargada: {local_metadata_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error descargando colección desde S3: {e}")
            return False
    
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
