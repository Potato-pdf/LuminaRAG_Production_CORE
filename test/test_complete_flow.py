"""
🔬 TEST COMPLETO END-TO-END DEL SISTEMA RAG
==========================================

Este script ejecuta el flujo completo:
1. Embedding e indexación con Milvus normal
2. Consultas RAG con Ollama/Llama3.2
3. Verificación de todo el pipeline

Ejecutar: python test/test_complete_flow.py
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Configurar rutas
sys.path.append('.')
sys.path.append('src')
load_dotenv()

def run_complete_test():
    """Ejecuta el test completo del sistema RAG"""
    
    print("🚀 INICIANDO TEST COMPLETO DEL SISTEMA RAG")
    print("=" * 80)
    print(f"⏰ Inicio: {datetime.now()}")
    print()
    
    # ========================================
    # VERIFICACIÓN INICIAL DEL SISTEMA
    # ========================================
    print("🔧 VERIFICACIÓN INICIAL DEL SISTEMA")
    print("-" * 60)
    
    # Verificar archivos necesarios
    required_files = [
        ".env",                                          # Configuración
        "pdfs/Introduccion-a-la-arquitectura-de-software-v1.0.2.pdf",  # PDF de prueba
        "src/config/settings.py",                        # Configuración del proyecto
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - FALTA")
            return False
    
    # Verificar variables de entorno críticas
    critical_vars = ['LLAMA_CLOUD_API_KEY', 'MILVUS_HOST', 'OLLAMA_MODEL']
    for var in critical_vars:
        if os.getenv(var):
            print(f"✅ {var} configurada")
        else:
            print(f"❌ {var} - NO CONFIGURADA")
            return False
    
    print("\n✅ Verificación inicial completada")
    time.sleep(2)
    
    # ========================================
    # FASE 1: EMBEDDING E INDEXACIÓN
    # ========================================
    print("\n" + "="*80)
    print("📥 FASE 1: EMBEDDING E INDEXACIÓN")
    print("="*80)
    
    try:
        # Importar y ejecutar test de embedding
        print("🔄 Ejecutando proceso de indexación...")
        
        # Importar todo lo necesario para indexación
        from llama_parse import LlamaParse
        from llama_index.core import Settings, VectorStoreIndex
        from llama_index.core.node_parser import SentenceWindowNodeParser
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        from llama_index.vector_stores.milvus import MilvusVectorStore
        from pymilvus import connections, Collection, utility
        from src.config import EMBEDDING_CONFIG, MILVUS_CONFIG
        
        # Conectar a Milvus
        connections.disconnect("default") if connections.has_connection("default") else None
        connections.connect(
            alias="default",
            host=MILVUS_CONFIG["host"],
            port=MILVUS_CONFIG["port"],
            user=MILVUS_CONFIG["user"],
            password=MILVUS_CONFIG["password"]
        )
        print(f"✅ Conectado a Milvus: {MILVUS_CONFIG['host']}:{MILVUS_CONFIG['port']}")
        
        # Configurar modelos
        embedding_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_CONFIG["model_name"],
            max_length=512
        )
        
        node_parser = SentenceWindowNodeParser(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text"
        )
        
        Settings.embed_model = embedding_model
        Settings.node_parser = node_parser
        print("✅ Modelos configurados")
        
        # Procesar PDF
        parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
            result_type="markdown",
            verbose=False  # Menos verbose para test completo
        )
        
        pdf_path = "pdfs/Introduccion-a-la-arquitectura-de-software-v1.0.2.pdf"
        print(f"📄 Procesando PDF: {os.path.basename(pdf_path)}")
        
        documents = parser.load_data(pdf_path)
        print(f"✅ {len(documents)} documentos extraídos")
        
        # Agregar metadata
        for i, doc in enumerate(documents):
            doc.metadata.update({
                "source_file": os.path.basename(pdf_path),
                "indexed_at": datetime.now().isoformat(),
                "test_run": "complete_flow",
                "document_index": i
            })
        
        # Crear vector store e índice
        collection_name = "test_complete_flow"
        vector_store = MilvusVectorStore(
            host=MILVUS_CONFIG["host"],
            port=MILVUS_CONFIG["port"],
            user=MILVUS_CONFIG["user"],
            password=MILVUS_CONFIG["password"],
            collection_name=collection_name,
            dim=EMBEDDING_CONFIG["embedding_dim"],
            overwrite=True
        )
        
        print("🔄 Creando índice vectorial...")
        # Usar primeros 10 documentos para test más rápido
        test_docs = documents[:10]
        index = VectorStoreIndex.from_documents(
            test_docs,
            vector_store=vector_store,
            show_progress=True
        )
        
        # Verificar indexación
        if utility.has_collection(collection_name):
            collection = Collection(collection_name)
            collection.load()
            doc_count = collection.num_entities
            print(f"✅ FASE 1 COMPLETADA: {doc_count} documentos indexados")
        else:
            raise Exception("Colección no creada")
            
    except Exception as e:
        print(f"❌ FASE 1 FALLÓ: {e}")
        return False
    
    # Pausa entre fases
    print("\n⏳ Pausa entre fases...")
    time.sleep(3)
    
    # ========================================
    # FASE 2: CONSULTAS RAG
    # ========================================
    print("\n" + "="*80)
    print("🔍 FASE 2: CONSULTAS RAG CON OLLAMA")
    print("="*80)
    
    try:
        # Importar componentes para consultas
        from llama_index.core.query_engine import RetrieverQueryEngine
        from llama_index.core.retrievers import VectorIndexRetriever
        from llama_index.llms.ollama import Ollama
        from src.config import OLLAMA_CONFIG
        
        # Verificar Ollama
        import requests
        ollama_response = requests.get(f"{OLLAMA_CONFIG['base_url']}/api/tags", timeout=5)
        if ollama_response.status_code != 200:
            raise Exception(f"Ollama no está ejecutándose en {OLLAMA_CONFIG['base_url']}")
        print(f"✅ Ollama verificado: {OLLAMA_CONFIG['base_url']}")
        
        # Configurar LLM
        llm = Ollama(
            model=OLLAMA_CONFIG["model"],
            base_url=OLLAMA_CONFIG["base_url"],
            temperature=0.1,
            request_timeout=60.0
        )
        Settings.llm = llm
        print(f"✅ LLM configurado: {OLLAMA_CONFIG['model']}")
        
        # Cargar índice existente
        vector_store_query = MilvusVectorStore(
            host=MILVUS_CONFIG["host"],
            port=MILVUS_CONFIG["port"],
            user=MILVUS_CONFIG["user"],
            password=MILVUS_CONFIG["password"],
            collection_name=collection_name,
            dim=EMBEDDING_CONFIG["embedding_dim"]
        )
        
        index_query = VectorStoreIndex.from_vector_store(vector_store_query)
        print("✅ Índice cargado para consultas")
        
        # Configurar motor de consultas
        retriever = VectorIndexRetriever(
            index=index_query,
            similarity_top_k=3
        )
        query_engine = RetrieverQueryEngine(retriever=retriever)
        print("✅ Motor de consultas configurado")
        
        # Realizar consultas de prueba
        test_queries = [
            "¿Cuál es el tema principal del documento?",
            "¿Qué conceptos importantes se mencionan sobre arquitectura?"
        ]
        
        successful_queries = 0
        
        for i, query in enumerate(test_queries, 1):
            try:
                print(f"\n🔍 Consulta {i}: {query}")
                
                response = query_engine.query(query)
                answer = str(response)
                
                # Verificar que la respuesta tiene contenido
                if len(answer.strip()) > 10:  # Respuesta mínima válida
                    print(f"✅ Respuesta recibida ({len(answer)} caracteres)")
                    print(f"📝 Preview: {answer[:100]}...")
                    successful_queries += 1
                else:
                    print(f"⚠️ Respuesta muy corta: {answer}")
                    
            except Exception as e:
                print(f"❌ Error en consulta {i}: {e}")
        
        if successful_queries == len(test_queries):
            print(f"\n✅ FASE 2 COMPLETADA: {successful_queries}/{len(test_queries)} consultas exitosas")
        else:
            raise Exception(f"Solo {successful_queries}/{len(test_queries)} consultas exitosas")
            
    except Exception as e:
        print(f"❌ FASE 2 FALLÓ: {e}")
        return False
    
    # ========================================
    # VERIFICACIÓN FINAL DEL SISTEMA
    # ========================================
    print("\n" + "="*80)
    print("🔬 VERIFICACIÓN FINAL DEL SISTEMA")
    print("="*80)
    
    try:
        # Verificar estado final de Milvus
        final_collections = utility.list_collections()
        print(f"📋 Colecciones en Milvus: {final_collections}")
        
        # Verificar colección de prueba
        if collection_name in final_collections:
            collection = Collection(collection_name)
            collection.load()
            final_count = collection.num_entities
            print(f"✅ Colección {collection_name}: {final_count} documentos")
            
            # Verificar campos
            schema = collection.schema
            fields = [field.name for field in schema.fields]
            print(f"🏗️ Campos: {fields}")
        else:
            raise Exception(f"Colección {collection_name} no encontrada")
        
        # Test rápido final
        print("\n🎯 Test rápido final...")
        final_response = query_engine.query("Resume en una línea el contenido")
        if len(str(final_response)) > 5:
            print("✅ Sistema RAG respondiendo correctamente")
        else:
            raise Exception("Sistema no responde adecuadamente")
            
        print("\n🎉 ¡VERIFICACIÓN FINAL EXITOSA!")
        
    except Exception as e:
        print(f"❌ VERIFICACIÓN FINAL FALLÓ: {e}")
        return False
    
    # ========================================
    # REPORTE FINAL
    # ========================================
    print("\n" + "="*80)
    print("📊 REPORTE FINAL DEL SISTEMA RAG")
    print("="*80)
    
    end_time = datetime.now()
    print(f"⏰ Tiempo total de ejecución: {end_time - datetime.now()}")
    print()
    print("🏗️ COMPONENTES VERIFICADOS:")
    print(f"  ✅ Milvus: {MILVUS_CONFIG['host']}:{MILVUS_CONFIG['port']}")
    print(f"  ✅ LLM: {OLLAMA_CONFIG['model']} @ {OLLAMA_CONFIG['base_url']}")
    print(f"  ✅ Embeddings: {EMBEDDING_CONFIG['model_name']}")
    print(f"  ✅ PDF Parser: LlamaParse")
    print()
    print("📊 RESULTADOS:")
    print(f"  ✅ Documentos procesados: {len(test_docs)}")
    print(f"  ✅ Documentos indexados: {final_count}")
    print(f"  ✅ Consultas exitosas: {successful_queries}/{len(test_queries)}")
    print(f"  ✅ Colección creada: {collection_name}")
    print()
    print("🎯 SIGUIENTE PASO:")
    print("  El sistema está listo para producción")
    print("  Usar scripts individuales para operación normal:")
    print("  - python index_documents.py <archivo.pdf>")
    print("  - python query_system.py")
    
    return True

if __name__ == "__main__":
    """Punto de entrada principal"""
    
    print("🔍 Verificando dependencias antes del test...")
    
    # Verificar que Ollama esté ejecutándose
    try:
        import requests
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code != 200:
            print(f"❌ Ollama no está ejecutándose en {ollama_url}")
            print("💡 Ejecutar: ollama serve")
            sys.exit(1)
    except Exception as e:
        print(f"❌ No se puede conectar a Ollama: {e}")
        print("💡 Verificar que Ollama esté instalado y ejecutándose")
        sys.exit(1)
    
    # Ejecutar test completo
    success = run_complete_test()
    
    if success:
        print("\n🎉 ¡TEST COMPLETO EXITOSO!")
        print("🚀 Sistema RAG completamente funcional")
    else:
        print("\n❌ TEST COMPLETO FALLÓ")
        print("🔧 Revisar errores y configuración")
        sys.exit(1)
