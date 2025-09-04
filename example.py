from urllib import response
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env si existe
env_path = Path(".") / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from db_milvus.connection import connect_milvus
from db_milvus.schemas.schema_comercial import create_schema_comercial
from embedding.multilingual import choice_embedding
from read_docs.read_pdf import read_pdf  # Mantenemos como fallback
from parse_docs import parse_documents    # Nuevo método con LlamaParse
from create_vectors.create_vector_milvus import create_vectors
from model_ai import connect_ollama
from create_index.create_index_llamaindex import create_index_llamaindex


def main():
    conn = connect_milvus()
    collection_name = create_schema_comercial()
    embedding_model = choice_embedding()
    print("Modelo de embedding seleccionado:", embedding_model)
    
    # Usar LlamaParse para procesar documentos si hay API key configurada
    try:
        documents = parse_documents(
            directory_path="pdfs",
            api_key=os.environ.get("LLAMA_CLOUD_API_KEY")
        )
        print("Documentos procesados con LlamaParse:", len(documents))
    except Exception as e:
        print(f"Error al usar LlamaParse: {e}")
        print("Usando método de lectura PDF tradicional como fallback...")
        documents = read_pdf()
    
    print("Documentos leídos:", documents)
    vector_store = create_vectors(collection_name, embedding_model)
    print("Vectores creados:", vector_store)
    llm = connect_ollama()
    index = create_index_llamaindex(documents, vector_store, embedding_model)
    print("Índice creado:", index)
    query = "segun el documento de cobranza dime como se hace la cobranza"

    # Usar el nuevo API de llama-index para consultar
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query(query)
    print(response)


main()