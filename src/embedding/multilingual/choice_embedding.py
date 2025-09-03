from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def choice_embedding():
    embedding_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-base")
    return embedding_model