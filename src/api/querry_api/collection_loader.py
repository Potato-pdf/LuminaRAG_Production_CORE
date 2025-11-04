"""
Módulo para carga de colecciones FAISS.
"""
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
import faiss

from src.config import STORAGE_CONFIG
from .s3_handler import S3Handler

logger = logging.getLogger(__name__)


class CollectionLoader:
    """Maneja la carga y cache de colecciones FAISS por empresa"""
    
    def __init__(self):
        self.collection_cache: Dict[str, Dict[str, Any]] = {}
        self.s3_handler = S3Handler()
    
    def load_collection(self, empresa: str, private: bool) -> Optional[Dict[str, Any]]:
        """
        Cargar sistema FAISS específico para una colección empresa_privacidad
        
        Args:
            empresa: Nombre de la empresa
            private: Si es colección privada o pública
            
        Returns:
            Diccionario con índice FAISS, metadata y configuración, o None si falla
        """
        privacidad_str = "private" if private else "public"
        collection_name = f"{empresa}_{privacidad_str}"

        # Verificar si ya está en cache
        if collection_name in self.collection_cache:
            return self.collection_cache[collection_name]

        try:
            # Buscar archivo FAISS de la colección
            faiss_dir = Path(STORAGE_CONFIG["base_dir"]) / "faiss_collections"
            faiss_path = faiss_dir / f"{collection_name}.faiss"
            metadata_path = faiss_dir / f"{collection_name}_metadata.json"

            # Si no existe localmente, intentar descargar desde S3
            if not faiss_path.exists():
                logger.info(f"Colección {collection_name} no encontrada localmente, descargando desde S3...")
                if not self.s3_handler.download_collection(collection_name, faiss_path, metadata_path):
                    logger.error(f"No se pudo descargar colección {collection_name} desde S3")
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
            self.collection_cache[collection_name] = collection_system

            logger.info(f"✅ Sistema FAISS cargado para colección: {collection_name}")
            return collection_system

        except Exception as e:
            logger.error(f"Error cargando sistema para colección {collection_name}: {e}")
            return None
    
    def clear_cache(self):
        """Limpiar cache de colecciones"""
        self.collection_cache.clear()
        logger.info("Cache de colecciones limpiado")
