from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

def create_index_llamaindex(documents, vector_store, embed_model):
    index =  VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store,
        embed_model=embed_model  # Aquí se pasa el modelo de embeddings explícitamente
    )
    return index
