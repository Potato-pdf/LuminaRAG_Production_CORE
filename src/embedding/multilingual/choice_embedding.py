from src.embedding.pooling.pooled_hugging_face_embendding import PooledHuggingFaceEmbedding

def choice_embedding():
    embedding_model = PooledHuggingFaceEmbedding(model_name="efederici/e5-base-multilingual-4096")
    return embedding_model