from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import numpy as np
from typing import List
from src.config import EMBEDDING_CONFIG

class PooledHuggingFaceEmbedding:
    def __init__(self, model_name: str):
        self.base_model = HuggingFaceEmbedding(model_name=model_name)#| modelo para embendings
        self.embed_dim = EMBEDDING_CONFIG["embedding_dim"]#| dimencion del embending
    
    def get_text_embedding(self, text: str) -> List[float]:# | crea el embending de un texto
        # Usar la API correcta de HuggingFaceEmbedding
        embedding = self.base_model.get_text_embedding(text)
        return embedding
    
    def get_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:#| iteracion de get_text_embedding para una lista de textost
        # Usar método batch nativo si está disponible, sino usar iteración
        try:
            return self.base_model.get_text_embedding_batch(texts)
        except AttributeError:
            # Fallback a iteración manual
            results = []
            for text in texts:
                results.append(self.get_text_embedding(text))
            return results  