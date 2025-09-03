from urllib import response
from db_milvus.connection import connect_milvus
from db_milvus.schemas.schema_comercial import create_schema_comercial
from embedding.multilingual import choice_embedding
from read_docs.read_pdf import read_pdf
from create_vectors.create_vector_milvus import create_vectors
from model_ai import connect_ollama
from create_index.create_index_llamaindex import create_index_llamaindex


def main():
    conn = connect_milvus()
    collection_name = create_schema_comercial()
    embedding_model = choice_embedding()
    print("Modelo de embedding seleccionado:", embedding_model)
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