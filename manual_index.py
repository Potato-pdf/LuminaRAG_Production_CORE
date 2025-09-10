#!/usr/bin/env python3
"""
🔧 INDEXADOR MANUAL PARA MILVUS
===============================

Script que inserta manualmente los datos en Milvus para asegurar que funcione.
"""

import os
import sys
import json
import pickle
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

def manual_indexing():
    """Indexación manual con inserción directa"""
    
    from pymilvus import connections, Collection, utility, DataType, CollectionSchema, FieldSchema
    from llama_index.core import Document, Settings
    from llama_index.core.node_parser import SentenceWindowNodeParser
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from src.parse_docs import parse_documents
    from src.document_graph import create_simple_rag_graph
    from src.config import CHUNKING_CONFIG, EMBEDDING_CONFIG, MILVUS_CONFIG, PATH_CONFIG, STORAGE_CONFIG, API_CONFIG
    
    print("🔧 INDEXACIÓN MANUAL DIRECTA")
    print("="*40)
    
    # 1. Conectar a Milvus
    print("🔌 Conectando a Milvus...")
    connections.connect(
        alias="default",
        host=MILVUS_CONFIG["host"],
        port=MILVUS_CONFIG["port"],
        user=MILVUS_CONFIG["user"],
        password=MILVUS_CONFIG["password"]
    )
    print("✅ Conectado a Milvus")
    
    # 2. Eliminar y crear colección
    collection_name = "lumina_manual"
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        print(f"🗑️ Colección {collection_name} eliminada")
    
    # Crear schema
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=512),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_CONFIG["embedding_dim"]),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="metadata", dtype=DataType.JSON)
    ]
    
    schema = CollectionSchema(fields=fields, description="Lumina Manual RAG")
    collection = Collection(name=collection_name, schema=schema)
    
    # Crear índice
    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="vector", index_params=index_params)
    print(f"✅ Colección {collection_name} creada con índice")
    
    # 3. Procesar documentos
    print("📄 Procesando documentos...")
    api_key = API_CONFIG["llama_cloud_api_key"]
    documents = parse_documents(api_key=api_key)
    print(f"✅ {len(documents)} documentos procesados")
    
    # 4. Configurar embedding
    print("🧠 Configurando embedding...")
    embedding_model = HuggingFaceEmbedding(
        model_name=EMBEDDING_CONFIG["model_name"],
        max_length=512,
        device="cpu"
    )
    print("✅ Embedding configurado")
    
    # 5. Crear chunks
    print("🔪 Creando chunks...")
    node_parser = SentenceWindowNodeParser(
        window_size=CHUNKING_CONFIG["chunk_window_size"],
        window_metadata_key="window",
        original_text_metadata_key="original_text"
    )
    
    nodes = node_parser.get_nodes_from_documents(documents)
    print(f"✅ {len(nodes)} chunks creados")
    
    # 6. Crear grafo
    print("🕸️ Creando grafo...")
    chunks_data = []
    for i, node in enumerate(nodes):
        chunk_data = {
            'id': node.node_id,
            'content': node.get_content(),
            'metadata': {
                'file_name': node.metadata.get('file_name', 'unknown'),
                'chunk_index': i,
                'node_id': node.node_id
            }
        }
        chunks_data.append(chunk_data)
    
    document_graph = create_simple_rag_graph(chunks_data)
    
    # Crear directorio si no existe
    import os
    os.makedirs(STORAGE_CONFIG["graphs_dir"], exist_ok=True)
    
    # Guardar grafo en carpeta específica
    graph_path = STORAGE_CONFIG["graph_path"]
    with open(graph_path, 'wb') as f:
        pickle.dump(document_graph, f)
    
    stats = document_graph.get_stats()
    print(f"✅ Grafo creado - Nodos: {stats['nodes']}, Conexiones: {stats['edges']}")
    
    # 7. Generar embeddings manualmente
    print("🔢 Generando embeddings...")
    texts = [node.get_content() for node in nodes]
    embeddings = embedding_model.get_text_embedding_batch(texts, show_progress=True)
    print(f"✅ {len(embeddings)} embeddings generados")
    
    # 8. Preparar datos para inserción
    print("📦 Preparando datos para inserción...")
    entities = []
    
    for i, (node, embedding) in enumerate(zip(nodes, embeddings)):
        entity = {
            "id": node.node_id,
            "vector": embedding,
            "text": node.get_content()[:65000],  # Truncar si es muy largo
            "metadata": {
                "file_name": node.metadata.get('file_name', 'unknown'),
                "chunk_index": i,
                "node_id": node.node_id,
                "page_label": node.metadata.get('page_label', '')
            }
        }
        entities.append(entity)
    
    print(f"✅ Datos preparados: {len(entities)} registros")
    
    # 9. Insertar en Milvus
    print("💾 Insertando en Milvus...")
    try:
        # Insertar por lotes para evitar problemas de memoria
        batch_size = 50
        total_inserted = 0
        
        for i in range(0, len(entities), batch_size):
            batch_entities = entities[i:i+batch_size]
            
            result = collection.insert(batch_entities)
            total_inserted += len(batch_entities)
            print(f"   Lote {i//batch_size + 1}: {len(batch_entities)} registros insertados")
        
        # Hacer flush para asegurar que se guarden
        collection.flush()
        print(f"✅ Flush completado")
        
        # Cargar colección
        collection.load()
        final_count = collection.num_entities
        
        print(f"✅ {final_count} documentos verificados en Milvus")
        
    except Exception as e:
        print(f"❌ Error en inserción: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 10. Resumen final
    print("\n" + "="*40)
    print("📊 RESUMEN FINAL")
    print("="*40)
    print(f"🗃️ Colección: {collection_name}")
    print(f"📊 Documentos insertados: {final_count}")
    print(f"🕸️ Grafo: {stats['nodes']} nodos, {stats['edges']} conexiones")
    print(f"🤖 Embedding: {EMBEDDING_CONFIG['model_name']}")
    print(f"💾 Grafo guardado: {graph_path}")
    print("="*40)
    
    if final_count > 0:
        print("🎉 ¡INDEXACIÓN MANUAL EXITOSA!")
        print(f"💡 Usar: python3 query_system.py --collection {collection_name} --interactive")
        return True
    else:
        print("❌ INDEXACIÓN MANUAL FALLÓ")
        return False

if __name__ == "__main__":
    success = manual_indexing()
    if not success:
        sys.exit(1)