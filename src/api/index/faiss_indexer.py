"""
Módulo para creación y gestión de índices FAISS.
"""
import logging
import json
from pathlib import Path
from typing import List, Any
from datetime import datetime
import faiss
import numpy as np

from src.config import STORAGE_CONFIG

logger = logging.getLogger(__name__)


class FAISSIndexer:
    """Crea y gestiona índices FAISS para colecciones de documentos"""
    
    def __init__(self):
        self.storage_dir = Path(STORAGE_CONFIG["base_dir"]) / "faiss_collections"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def create_index(
        self,
        empresa: str,
        private: bool,
        nodes: List[Any],
        embeddings: List[List[float]]
    ) -> tuple[str, Path, Path]:
        """
        Crear índice FAISS para una colección específica
        
        Args:
            empresa: Nombre de la empresa
            private: Si es colección privada o pública
            nodes: Nodos con contenido y metadata
            embeddings: Embeddings de los nodos
            
        Returns:
            Tupla con (collection_name, faiss_path, metadata_path)
        """
        privacidad_str = "private" if private else "public"
        collection_name = f"{empresa}_{privacidad_str}"
        
        faiss_path = self.storage_dir / f"{collection_name}.faiss"
        metadata_path = self.storage_dir / f"{collection_name}_metadata.json"
        
        # Crear índice FAISS
        dimension = len(embeddings[0]) if embeddings else 768
        faiss_index = faiss.IndexFlatIP(dimension)
        
        # Agregar embeddings
        embeddings_array = np.array(embeddings, dtype=np.float32)
        faiss_index.add(embeddings_array)
        
        # Guardar índice FAISS
        faiss.write_index(faiss_index, str(faiss_path))
        logger.info(f"💾 Índice FAISS creado: {faiss_path}")
        
        # Crear y guardar metadata
        metadata = self._create_metadata(collection_name, empresa, private, nodes)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Metadata guardada: {metadata_path}")
        
        return collection_name, faiss_path, metadata_path
    
    def _create_metadata(
        self,
        collection_name: str,
        empresa: str,
        private: bool,
        nodes: List[Any]
    ) -> dict:
        """Crear estructura de metadata para la colección"""
        # Preparar chunks con contenido completo
        chunks_data = []
        doc_info = {}
        
        for i, node in enumerate(nodes):
            file_name = node.metadata.get('file_name', 'unknown')
            
            # Guardar chunk completo con su contenido
            chunks_data.append({
                "id": i,
                "file_name": file_name,
                "content": node.get_content(),
                "empresa": empresa,
                "private": private
            })
            
            # Agregar información de documento
            if file_name not in doc_info:
                doc_info[file_name] = {
                    "file_name": file_name,
                    "empresa": empresa,
                    "private": private,
                    "chunk_count": 0
                }
            doc_info[file_name]["chunk_count"] += 1
        
        return {
            "collection_name": collection_name,
            "empresa": empresa,
            "private": private,
            "document_count": len(doc_info),
            "chunk_count": len(nodes),
            "created_at": datetime.now().isoformat(),
            "chunks": chunks_data,
            "documents": list(doc_info.values())
        }
