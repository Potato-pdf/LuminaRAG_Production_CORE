#!/usr/bin/env python3
"""
🌳 INDEXADOR JERÁRQUICO PRINCIPAL
================================

Sistema de indexación principal que usa arquitectura jerárquica:
- 1 grafo por documento (árbol con raíz)
- Meta-grafo conectando raíces
- Milvus con campos jerárquicos
- PageRank jerárquico
"""

import os
import sys
import pickle
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

def main():
    """Indexación principal con arquitectura jerárquica"""
    
    from pymilvus import connections, Collection, utility, DataType, CollectionSchema, FieldSchema
    from llama_index.core import Document, Settings
    from llama_index.core.node_parser import SentenceWindowNodeParser
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from src.parse_docs import parse_documents
    from src.document_graph import create_hierarchical_rag_graph  # NUEVA ARQUITECTURA
    from src.config import CHUNKING_CONFIG, EMBEDDING_CONFIG, MILVUS_CONFIG, PATH_CONFIG, STORAGE_CONFIG, API_CONFIG
    
    print("🌳 INDEXADOR JERÁRQUICO LUMINA")
    print("="*50)
    
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
    
    # 2. Configurar colección jerárquica
    collection_name = "lumina_hierarchical"
    setup_hierarchical_collection(collection_name)
    
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
    
    # 6. Crear arquitectura jerárquica
    print("🌳 Construyendo arquitectura jerárquica...")
    chunks_data = prepare_chunks_data(nodes)
    hierarchical_graph = create_hierarchical_rag_graph(chunks_data)
    
    # Guardar grafo jerárquico
    save_hierarchical_graph(hierarchical_graph)
    
    # 7. Generar embeddings
    print("🔢 Generando embeddings...")
    embeddings = generate_embeddings(nodes, embedding_model)
    
    # 8. Insertar datos jerárquicos en Milvus
    print("💾 Insertando datos jerárquicos...")
    success = insert_hierarchical_data(collection_name, nodes, embeddings, hierarchical_graph)
    
    if not success:
        print("❌ Error en inserción de datos jerárquicos")
        return False
    
    # 9. Crear sistema FAISS-GPU optimizado
    print("🚀 Creando sistema FAISS-GPU optimizado...")
    faiss_success = create_faiss_system(hierarchical_graph)
    
    # 10. Resumen final
    print_final_summary(collection_name, hierarchical_graph, faiss_success)
    
    return True

def setup_hierarchical_collection(collection_name: str):
    """Configurar colección Milvus con campos jerárquicos"""
    from pymilvus import Collection, utility, DataType, CollectionSchema, FieldSchema
    from src.config import EMBEDDING_CONFIG
    
    # Eliminar colección si existe
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        print(f"🗑️ Colección '{collection_name}' eliminada")
    
    # Definir campos jerárquicos
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=500, is_primary=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_CONFIG["embedding_dim"]),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="metadata", dtype=DataType.JSON),
        # Campos jerárquicos especializados
        FieldSchema(name="document_name", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="is_root", dtype=DataType.BOOL),
        FieldSchema(name="tree_level", dtype=DataType.INT64),
        FieldSchema(name="parent_chunk", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="hierarchical_importance", dtype=DataType.FLOAT)
    ]
    
    schema = CollectionSchema(fields=fields, description="Colección jerárquica con árboles por documento")
    collection = Collection(name=collection_name, schema=schema)
    
    # Crear índices
    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    collection.create_index(field_name="vector", index_params=index_params)
    
    print(f"✅ Colección jerárquica '{collection_name}' creada")

def prepare_chunks_data(nodes) -> list:
    """Preparar datos de chunks para el grafo jerárquico"""
    chunks_data = []
    
    for node in nodes:
        chunk_data = {
            'id': node.node_id,
            'content': node.get_content(),
            'metadata': {
                'file_name': node.metadata.get('file_name', 'unknown'),
                'page_label': node.metadata.get('page_label', ''),
                'chunk_index': len(chunks_data)
            }
        }
        chunks_data.append(chunk_data)
    
    return chunks_data

def save_hierarchical_graph(hierarchical_graph):
    """Guardar grafo jerárquico"""
    from src.config import STORAGE_CONFIG
    
    hierarchical_path = STORAGE_CONFIG["graph_path"].replace(".pkl", "_hierarchical.pkl")
    
    with open(hierarchical_path, 'wb') as f:
        pickle.dump(hierarchical_graph, f)
    
    print(f"💾 Grafo jerárquico guardado: {hierarchical_path}")

def generate_embeddings(nodes, embedding_model):
    """Generar embeddings para los chunks"""
    embeddings = []
    for node in nodes:
        embedding = embedding_model.get_text_embedding(node.get_content())
        embeddings.append(embedding)
    return embeddings

def insert_hierarchical_data(collection_name: str, nodes, embeddings, hierarchical_graph):
    """Insertar datos con información jerárquica en Milvus"""
    from pymilvus import Collection
    
    collection = Collection(collection_name)
    entities = []
    document_roots = hierarchical_graph.get_document_roots()
    
    for i, (node, embedding) in enumerate(zip(nodes, embeddings)):
        # Obtener información jerárquica
        doc_name = hierarchical_graph.find_document_for_chunk(node.node_id)
        is_root = node.node_id in document_roots.values()
        
        # Calcular información del árbol
        tree_info = calculate_tree_info(node.node_id, hierarchical_graph)
        
        # Calcular importancia jerárquica
        hierarchical_importance = calculate_hierarchical_importance(
            node.node_id, hierarchical_graph, is_root
        )
        
        entity = {
            "id": node.node_id,
            "vector": embedding,
            "text": node.get_content()[:65000],
            "metadata": {
                "file_name": node.metadata.get('file_name', 'unknown'),
                "chunk_index": i,
                "node_id": node.node_id,
                "page_label": node.metadata.get('page_label', ''),
                "document_name": doc_name or 'unknown',
                "is_document_root": is_root,
                "tree_level": tree_info['level'],
                "parent_chunk": tree_info['parent'],
                "hierarchical_importance": hierarchical_importance
            },
            # Campos directos para búsquedas eficientes
            "document_name": doc_name or 'unknown',
            "is_root": is_root,
            "tree_level": tree_info['level'],
            "parent_chunk": tree_info['parent'] or '',
            "hierarchical_importance": hierarchical_importance
        }
        entities.append(entity)
    
    # Insertar por lotes
    print("💾 Insertando en Milvus...")
    try:
        batch_size = 50
        total_inserted = 0
        
        for i in range(0, len(entities), batch_size):
            batch_entities = entities[i:i+batch_size]
            result = collection.insert(batch_entities)
            total_inserted += len(batch_entities)
            print(f"   Lote {i//batch_size + 1}: {len(batch_entities)} registros insertados")
        
        collection.flush()
        print(f"✅ Flush completado")
        
        collection.load()
        final_count = collection.num_entities
        
        print(f"✅ {final_count} documentos verificados en Milvus")
        return True
        
    except Exception as e:
        print(f"❌ Error en inserción: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_tree_info(chunk_id: str, hierarchical_graph) -> dict:
    """Calcular información del árbol para un chunk"""
    # Obtener vecinos para determinar nivel y padre
    doc_name = hierarchical_graph.find_document_for_chunk(chunk_id)
    if not doc_name:
        return {'level': 0, 'parent': None}
    
    # Para simplicidad, usar la metadata si está disponible
    try:
        # Intentar calcular desde el grafo
        doc_root = hierarchical_graph.get_document_roots().get(doc_name)
        if doc_root == chunk_id:
            return {'level': 0, 'parent': None}  # Es raíz
        
        # Encontrar el padre (nodo que apunta a este chunk)
        graph = hierarchical_graph._manager.graph
        predecessors = list(graph.predecessors(chunk_id))
        parent = predecessors[0] if predecessors else None
        
        # Calcular nivel aproximado
        if parent:
            parent_level = calculate_tree_info(parent, hierarchical_graph)['level']
            level = parent_level + 1
        else:
            level = 1
        
        return {'level': min(level, 10), 'parent': parent}  # Limitar nivel máximo
    except:
        return {'level': 1, 'parent': None}

def calculate_hierarchical_importance(chunk_id: str, hierarchical_graph, is_root: bool) -> float:
    """Calcular importancia jerárquica usando PageRank"""
    try:
        # Intentar obtener PageRank desde el grafo jerárquico
        if hasattr(hierarchical_graph, 'get_hierarchical_analyzer'):
            analyzer = hierarchical_graph.get_hierarchical_analyzer()
            if analyzer:
                scores = analyzer.calculate_pagerank()
                score = scores.get(chunk_id, 1.0)
                return float(score)
        
        # Fallback: dar mayor peso a raíces
        return 1.5 if is_root else 1.0
    except:
        return 1.5 if is_root else 1.0

def create_faiss_system(hierarchical_graph) -> bool:
    """Crear sistema FAISS-GPU desde el grafo jerárquico"""
    try:
        from src.FAISS.faiss_integration import create_faiss_system_from_hierarchical, save_faiss_system
        import faiss
        
        # Mostrar información de GPU
        gpu_count = faiss.get_num_gpus()
        print(f"🔍 GPUs detectadas: {gpu_count}")
        
        # Crear sistema FAISS
        faiss_system = create_faiss_system_from_hierarchical(hierarchical_graph)
        
        if not faiss_system.is_built:
            print("❌ Error creando sistema FAISS-GPU")
            return False
        
        # Guardar sistema FAISS
        success = save_faiss_system(faiss_system)
        
        if success:
            print("✅ Sistema FAISS-GPU creado y guardado exitosamente")
            faiss_system.print_system_summary()
        
        return success
        
    except Exception as e:
        print(f"❌ Error creando sistema FAISS-GPU: {e}")
        print("💡 Tip: Verificar instalación de CUDA para aceleración GPU")
        return False

def print_final_summary(collection_name: str, hierarchical_graph, faiss_success: bool = False):
    """Imprimir resumen final del indexing"""
    from src.config import EMBEDDING_CONFIG
    
    stats = hierarchical_graph.get_hierarchical_stats()
    
    print("\n" + "="*60)
    print("📊 RESUMEN INDEXACIÓN JERÁRQUICA")
    print("="*60)
    print(f"🗃️ Colección Milvus: {collection_name}")
    print(f"📊 Total chunks: {stats['total_chunks']}")
    print(f"📄 Documentos: {stats['documents_count']}")
    print(f"🌿 Raíces de documentos: {stats['document_roots']}")
    print(f"🔗 Conexiones del grafo: {stats['total_connections']}")
    print(f"🌐 Meta-conexiones: {stats['meta_graph_connections']}")
    print(f"🤖 Modelo embedding: {EMBEDDING_CONFIG['model_name']}")
    
    print(f"\n🌳 ARQUITECTURA JERÁRQUICA:")
    hierarchical_graph.print_hierarchy_summary()
    
    # Información del sistema FAISS
    if faiss_success:
        print(f"\n🚀 SISTEMA FAISS-GPU:")
        print(f"   ✅ Índice FAISS-GPU creado exitosamente")
        print(f"   🔍 Búsqueda optimizada por raíces")
        print(f"   ⚡ Aceleración GPU disponible")
        print(f"   💾 Rendimiento mejorado para consultas")
    
    print(f"\n🎉 ¡INDEXACIÓN COMPLETA FINALIZADA!")
    print(f"💡 Sistemas disponibles:")
    print(f"   🌳 python3 query.py        # Sistema jerárquico tradicional")
    if faiss_success:
        print(f"   🚀 python3 query_faiss.py   # Sistema FAISS-GPU optimizado (RECOMENDADO)")
    print("="*60)

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Indexación cancelada")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error en indexación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)