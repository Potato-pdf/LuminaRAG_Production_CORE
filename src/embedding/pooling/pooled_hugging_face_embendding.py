from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import numpy as np
from typing import List
from src.config import EMBEDDING_CONFIG

class PooledHuggingFaceEmbedding:
    def __init__(self, model_name: str):
        self.base_model = HuggingFaceEmbedding(model_name=model_name)#| modelo para embendings
        self.embed_dim = EMBEDDING_CONFIG["embedding_dim"]#| dimencion del embending
    
    def get_text_embedding(self, text: str) -> List[float]:# | crea el embending de un texto
        token_embeddings = self.base_model._get_raw_embedding(text)
        mean_pooled = np.mean(token_embeddings, axis=0).tolist()#| saca el promedio columna por columna y lo almacena en una lista
        return mean_pooled
    
    def get_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:#| iteracion de get_text_embedding para una lista de textost
        results = []
        for text in texts:
            results.append(self.get_text_embedding(text))
        return results  