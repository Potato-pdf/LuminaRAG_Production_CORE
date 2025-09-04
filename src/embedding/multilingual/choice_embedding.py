from src.embedding.pooling.pooled_hugging_face_embendding import PooledHuggingFaceEmbedding
from src.config import EMBEDDING_CONFIG

def choice_embedding():
    # Usamos el modelo definido en la configuración centralizada
    embedding_model = PooledHuggingFaceEmbedding(model_name=EMBEDDING_CONFIG["model_name"])
    return embedding_model