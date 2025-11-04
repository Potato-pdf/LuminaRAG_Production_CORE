"""
Módulo para generación de embeddings de documentos.
"""
import logging
from typing import List, Any

from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from src.config import CHUNKING_CONFIG, EMBEDDING_CONFIG

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Genera chunks y embeddings de documentos"""
    
    def __init__(self):
        self.embedding_model = None
        self.node_parser = None
        self._initialized = False
    
    def initialize(self):
        """Inicializar modelo de embeddings y parser de nodos"""
        if self._initialized:
            return
        
        logger.info("Inicializando EmbeddingGenerator...")
        
        # Configurar embedding model
        self.embedding_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_CONFIG["model_name"],
            max_length=512,
            device="cpu"
        )
        
        # Configurar node parser
        self.node_parser = SentenceWindowNodeParser(
            window_size=CHUNKING_CONFIG["chunk_window_size"],
            window_metadata_key="window",
            original_text_metadata_key="original_text"
        )
        
        self._initialized = True
        logger.info("✅ EmbeddingGenerator inicializado")
    
    def generate_chunks_and_embeddings(
        self, 
        documents: List[Any]
    ) -> tuple[List[Any], List[List[float]]]:
        """
        Generar chunks y sus embeddings
        
        Args:
            documents: Lista de documentos a procesar
            
        Returns:
            Tupla con (nodes, embeddings)
        """
        if not self._initialized:
            self.initialize()
        
        # Crear chunks
        nodes = self.node_parser.get_nodes_from_documents(documents)
        logger.info(f"✅ {len(nodes)} chunks creados")
        
        # Generar embeddings
        embeddings = []
        for node in nodes:
            embedding = self.embedding_model.get_text_embedding(node.get_content())
            embeddings.append(embedding)
        
        logger.info(f"✅ {len(embeddings)} embeddings generados")
        
        return nodes, embeddings
