
from llama_index.vector_stores.milvus import MilvusVectorStore
def create_vectors(collection, embedding_model):
    vector_store = MilvusVectorStore(
        collection_name=collection,
        embedding_model=embedding_model,
        dim=768,  # Dimensión del modelo intfloat/multilingual-e5-base
        embedding_field="embedding"  # Nombre estándar para el campo de embedding
    )
    return vector_store

