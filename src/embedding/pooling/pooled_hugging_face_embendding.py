from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import numpy as np
from typing import List

class PooledHuggingFaceEmbedding:
    def __init__(self, model_name: str):
        self.base_model = HuggingFaceEmbedding(model_name=model_name)
        self.embed_dim = 768
    
    def get_text_embedding(self, text: str) -> List[float]:
        token_embeddings = self.base_model._get_raw_embedding(text)
        
        mean_pooled = np.mean(token_embeddings, axis=0).tolist()
        return mean_pooled
    
    def get_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            results.append(self.get_text_embedding(text))
        return results
