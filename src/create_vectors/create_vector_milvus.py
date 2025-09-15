from llama_index.vector_stores.milvus import MilvusVectorStore

def create_vectors(collection, embedding_model): #funcion para crear el vector store de milvus
    vector_store = MilvusVectorStore(
        collection_name=collection, #| Nombre de la colección en Milvus
        embedding_model=embedding_model, #| Modelo de embedding
        dim=768,  # Dimensión del modelo intfloat/multilingual-e5-base
        embedding_field="embedding"  # Nombre estándar para el campo de embedding
    )
    return vector_store #| Retorna el vector store creado 

