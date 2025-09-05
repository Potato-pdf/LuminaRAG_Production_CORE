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
from src.config import CHUNKING_CONFIG, OLLAMA_CONFIG, PATH_CONFIG

# Import del sistema de grafo integrado
from src.document_graph import create_simple_rag_graph


def extract_chunks_from_index(index):
    """Extrae chunks del índice vectorial para crear el grafo"""
    #| Extrayendo chunks del índice vectorial para el grafo de documentos
    chunks_data = []
    nodes = list(index.docstore.docs.values())
    
    for i, node in enumerate(nodes):
        chunk_data = {
            'chunk_id': node.node_id,
            'content': node.get_content(),
            'metadata': {
                'file_name': node.metadata.get('file_name', 'unknown'),
                'file_path': node.metadata.get('file_path', ''),
                'page_label': node.metadata.get('page_label', ''),
                'window': node.metadata.get('window', ''),
                'original_text': node.metadata.get('original_text', ''),
                'chunk_index': i
            }
        }
        chunks_data.append(chunk_data)
    
    #| {len(chunks_data)} chunks extraídos para el grafo
    return chunks_data


def hybrid_query_with_graph(query_engine, document_graph, query, use_graph_context=True, top_k_graph=3):
    """Realiza consulta híbrida usando vectores + grafo para contexto"""
    #| Procesando consulta híbrida: vector search + graph context
    
    # 1. Consulta vectorial tradicional
    vector_response = query_engine.query(query)
    
    # 2. Si se solicita, enriquecer con contexto del grafo
    if use_graph_context and document_graph:
        #| Enriqueciendo respuesta con contexto del grafo de documentos
        
        # Obtener chunks más importantes del grafo
        important_chunks = document_graph.get_most_important_chunks(top_k=top_k_graph)
        
        # Construir contexto adicional del grafo
        graph_context = "\n\nContexto adicional del grafo de documentos:\n"
        for chunk_id, importance in important_chunks:
            content = document_graph.get_chunk_content(chunk_id)
            if content:
                graph_context += f"[Relevancia: {importance:.3f}] {content[:200]}...\n"
        
        # Consulta enriquecida con contexto del grafo
        enriched_query = f"{query}\n\n{graph_context}"
        enriched_response = query_engine.query(enriched_query)
        
        #| Respuesta enriquecida con contexto del grafo generada
        return str(enriched_response)
    
    #| Respuesta solo con búsqueda vectorial
    return str(vector_response)


def main():
    #| === CONFIGURACIÓN DE INFRAESTRUCTURA ===
    conn = connect_milvus()
    collection_name = create_schema_comercial()
    embedding_model = choice_embedding()
    print("Modelo de embedding seleccionado:", embedding_model)
    
    #| === PARSEO DE DOCUMENTOS ===
    try:
        documents = parse_documents(
            directory_path=PATH_CONFIG["pdf_directory"],
            api_key=os.environ.get("LLAMA_CLOUD_API_KEY") or os.environ.get("LLAMA_API_KEY")
        )
        print("Documentos procesados con LlamaParse:", len(documents))
    except Exception as e:
        print(f"Error al usar LlamaParse: {e}")
        print("Usando método de lectura PDF tradicional como fallback...")
        documents = read_pdf()
    
    print("Documentos leídos:", documents)
    
    #| === CREACIÓN DE VECTORES E ÍNDICE ===
    vector_store = create_vectors(collection_name, embedding_model)
    print("Vectores creados:", vector_store)
    llm = connect_ollama()
    
    # Crear índice usando configuración centralizada de chunking
    index = create_index_llamaindex(
        documents=documents, 
        vector_store=vector_store, 
        embed_model=embedding_model,
        **CHUNKING_CONFIG  # Usamos los parámetros desde la configuración centralizada
    )
    print("Índice creado:", index)
    
    #| === INTEGRACIÓN DEL GRAFO DE DOCUMENTOS ===
    # Extraer chunks del índice para crear el grafo
    chunks_data = extract_chunks_from_index(index)
    
    # Crear grafo de documentos para preservar estructura y contexto
    document_graph = create_simple_rag_graph(chunks_data)
    print(f"Grafo de documentos creado: {document_graph.chunk_count} chunks")
    
    #| === CONSULTA HÍBRIDA (VECTORES + GRAFO) ===
    query = "segun el documento de cobranza dime como se hace la cobranza"
    
    # Crear query engine tradicional
    query_engine = index.as_query_engine(llm=llm)
    
    # Realizar consulta híbrida con contexto del grafo
    response = hybrid_query_with_graph(
        query_engine=query_engine,
        document_graph=document_graph,
        query=query,
        use_graph_context=True,  # Usar contexto del grafo
        top_k_graph=3           # Top 3 chunks más importantes como contexto
    )
    
    print("=== RESPUESTA FINAL (Vector Search + Graph Context) ===")
    print(response)


main()