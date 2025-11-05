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
        embeddings: List[List[float]],
        incremental: bool = False
    ) -> tuple[str, Path, Path]:
        """
        Crear o actualizar índice FAISS para una colección específica
        
        Args:
            empresa: Nombre de la empresa
            private: Si es colección privada o pública
            nodes: Nodos con contenido y metadata
            embeddings: Embeddings de los nodos
            incremental: Si True, agrega al índice existente
            
        Returns:
            Tupla con (collection_name, faiss_path, metadata_path)
        """
        privacidad_str = "private" if private else "public"
        collection_name = f"{empresa}_{privacidad_str}"
        
        faiss_path = self.storage_dir / f"{collection_name}.faiss"
        metadata_path = self.storage_dir / f"{collection_name}_metadata.json"
        
        dimension = len(embeddings[0]) if embeddings else 768
        
        # Si es incremental y existe el índice, cargarlo
        if incremental and faiss_path.exists() and metadata_path.exists():
            logger.info(f"🔄 Actualizando índice existente {collection_name}")
            faiss_index = faiss.read_index(str(faiss_path))
            
            # Cargar metadata existente
            with open(metadata_path, 'r', encoding='utf-8') as f:
                existing_metadata = json.load(f)
            
            # Agregar nuevos embeddings
            embeddings_array = np.array(embeddings, dtype=np.float32)
            faiss_index.add(embeddings_array)
            
            # Actualizar metadata (agregar nuevos chunks)
            new_metadata = self._update_metadata(existing_metadata, empresa, private, nodes)
        else:
            # Crear nuevo índice
            logger.info(f"🆕 Creando nuevo índice {collection_name}")
            faiss_index = faiss.IndexFlatIP(dimension)
            
            # Agregar embeddings
            embeddings_array = np.array(embeddings, dtype=np.float32)
            faiss_index.add(embeddings_array)
            
            # Crear metadata nueva
            new_metadata = self._create_metadata(collection_name, empresa, private, nodes)
        
        # Guardar índice FAISS
        faiss.write_index(faiss_index, str(faiss_path))
        logger.info(f"💾 Índice FAISS guardado: {faiss_path}")
        
        # Guardar metadata actualizada
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(new_metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Metadata guardada: {metadata_path}")
        
        return collection_name, faiss_path, metadata_path
    
    def _update_metadata(
        self,
        existing_metadata: dict,
        empresa: str,
        private: bool,
        new_nodes: List[Any]
    ) -> dict:
        """Actualizar metadata con nuevos nodos"""
        # Obtener ID base para nuevos chunks
        base_id = len(existing_metadata.get("chunks", []))
        
        # Agregar nuevos chunks
        for i, node in enumerate(new_nodes):
            # Obtener file_name de metadata del nodo
            file_name = None
            if hasattr(node, 'metadata'):
                if isinstance(node.metadata, dict):
                    file_name = node.metadata.get('file_name')
                else:
                    file_name = getattr(node.metadata, 'file_name', None)
            
            # Si no hay file_name, saltar este chunk (error)
            if not file_name or file_name == 'unknown':
                logger.warning(f"Chunk {base_id + i} sin file_name válido, omitiendo...")
                continue
            
            existing_metadata["chunks"].append({
                "id": base_id + i,
                "file_name": file_name,
                "content": node.get_content(),
                "empresa": empresa,
                "private": private
            })
            
            # Actualizar documento info
            doc_found = False
            for doc in existing_metadata.get("documents", []):
                if doc["file_name"] == file_name:
                    doc["chunk_count"] += 1
                    doc_found = True
                    break
            
            if not doc_found:
                existing_metadata.setdefault("documents", []).append({
                    "file_name": file_name,
                    "empresa": empresa,
                    "private": private,
                    "chunk_count": 1
                })
        
        # Actualizar contadores
        existing_metadata["chunk_count"] = len(existing_metadata["chunks"])
        existing_metadata["document_count"] = len(existing_metadata["documents"])
        existing_metadata["updated_at"] = datetime.now().isoformat()
        
        return existing_metadata
    
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
            # Obtener file_name de metadata del nodo
            file_name = None
            if hasattr(node, 'metadata'):
                if isinstance(node.metadata, dict):
                    file_name = node.metadata.get('file_name')
                else:
                    file_name = getattr(node.metadata, 'file_name', None)
            
            # Si no hay file_name válido, saltar este chunk
            if not file_name or file_name == 'unknown':
                logger.warning(f"Chunk {i} sin file_name válido, omitiendo...")
                continue
            
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
