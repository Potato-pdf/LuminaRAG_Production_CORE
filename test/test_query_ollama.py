"""
🔬 TEST DE CONSULTAS RAG CON OLLAMA/LLAMA3.2
============================================

Este script prueba todo el flujo de consultas:
1. Conectar a Milvus normal
2. Cargar índice vectorial existente
3. Configurar Ollama/Llama3.2
4. Realizar consultas RAG completas

Ejecutar DESPUÉS de test_embedding_milvus.py
Comando: python test/test_query_ollama.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Configurar rutas para importar módulos del proyecto
sys.path.append('.')
sys.path.append('src')

# Cargar variables de entorno desde .env
load_dotenv()

def test_query_with_ollama():
    """Función principal que prueba todo el flujo de consultas RAG"""
    
    print("🚀 INICIANDO TEST DE CONSULTAS RAG CON OLLAMA")
    print("=" * 70)
    print(f"⏰ Timestamp: {datetime.now()}")
    print()
    
    # ========================================
    # PASO 1: VERIFICAR CONFIGURACIÓN
    # ========================================
    print("1️⃣ VERIFICANDO CONFIGURACIÓN...")
    print("-" * 40)
    
    # Verificar variables específicas para consultas
    required_vars = [
        'MILVUS_HOST',            # Para conectar a Milvus
        'MILVUS_PORT', 
        'MILVUS_USER',
        'MILVUS_PASSWORD',
        'OLLAMA_BASE_URL',        # Para conectar a Ollama
        'OLLAMA_MODEL',           # Modelo LLM (llama3.2)
        'EMBEDDING_MODEL'         # Modelo embeddings (debe ser el mismo que en indexación)
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NO ENCONTRADA")
            return False
    
    print()
    
    # ========================================
    # PASO 2: IMPORTAR LIBRERÍAS PARA CONSULTAS
    # ========================================
    print("2️⃣ IMPORTANDO LIBRERÍAS...")
    print("-" * 40)
    
    try:
        # Importar componentes core de LlamaIndex
        from llama_index.core import Settings, VectorStoreIndex
        print("✅ LlamaIndex Core importado")
        
        # Importar motor de consultas y retriever
        from llama_index.core.query_engine import RetrieverQueryEngine
        from llama_index.core.retrievers import VectorIndexRetriever
        print("✅ Query Engine y Retriever importados")
        
        # Importar LLM de Ollama
        from llama_index.llms.ollama import Ollama
        print("✅ Ollama LLM importado")
        
        # Importar embedding model (debe ser el mismo que para indexación)
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        print("✅ HuggingFace Embeddings importado")
        
        # Importar Milvus vector store
        from llama_index.vector_stores.milvus import MilvusVectorStore
        print("✅ Milvus VectorStore importado")
        
        # Importar cliente directo de Milvus
        from pymilvus import connections, Collection, utility
        print("✅ PyMilvus importado")
        
        # Importar configuración del proyecto
        from src.config import EMBEDDING_CONFIG, MILVUS_CONFIG, OLLAMA_CONFIG
        print("✅ Configuración del proyecto importada")
        
    except ImportError as e:
        print(f"❌ Error importando librerías: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 3: VERIFICAR OLLAMA ESTÁ EJECUTÁNDOSE
    # ========================================
    print("3️⃣ VERIFICANDO OLLAMA...")
    print("-" * 40)
    
    try:
        import requests
        
        # Probar conexión a Ollama
        ollama_url = OLLAMA_CONFIG["base_url"]
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Ollama está ejecutándose en {ollama_url}")
            
            # Verificar que el modelo está disponible
            models = response.json()
            available_models = [model['name'] for model in models.get('models', [])]
            
            target_model = OLLAMA_CONFIG["model"]
            if any(target_model in model for model in available_models):
                print(f"✅ Modelo {target_model} está disponible")
            else:
                print(f"⚠️ Modelo {target_model} no encontrado")
                print(f"📋 Modelos disponibles: {available_models}")
                print(f"💡 Ejecutar: ollama pull {target_model}")
        else:
            print(f"❌ Ollama no responde en {ollama_url}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando Ollama: {e}")
        print("💡 Verificar que Ollama esté ejecutándose: ollama serve")
        return False
    
    print()
    
    # ========================================
    # PASO 4: CONECTAR A MILVUS
    # ========================================
    print("4️⃣ CONECTANDO A MILVUS...")
    print("-" * 40)
    
    try:
        # Desconectar conexiones previas
        try:
            connections.disconnect("default")
        except:
            pass
        
        # Conectar a Milvus usando configuración
        connections.connect(
            alias="default",
            host=MILVUS_CONFIG["host"],               # Host del servidor Milvus
            port=MILVUS_CONFIG["port"],               # Puerto (19530)
            user=MILVUS_CONFIG["user"],               # Usuario
            password=MILVUS_CONFIG["password"]        # Password
        )
        
        print(f"✅ Conectado a Milvus en {MILVUS_CONFIG['host']}:{MILVUS_CONFIG['port']}")
        
        # Verificar que existe la colección de prueba
        collection_name = "test_arquitectura_completa"
        
        if utility.has_collection(collection_name):
            collection = Collection(collection_name)
            collection.load()
            doc_count = collection.num_entities
            print(f"✅ Colección encontrada: {collection_name} ({doc_count} documentos)")
        else:
            print(f"❌ Colección {collection_name} no existe")
            print("💡 Ejecutar primero: python test/test_embedding_milvus.py")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando a Milvus: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 5: CONFIGURAR MODELOS (LLM + EMBEDDINGS)
    # ========================================
    print("5️⃣ CONFIGURANDO MODELOS...")
    print("-" * 40)
    
    try:
        # Configurar modelo de embeddings (DEBE ser el mismo que en indexación)
        embedding_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_CONFIG["model_name"],    # Mismo modelo que indexación
            max_length=512
        )
        print(f"✅ Embedding model: {EMBEDDING_CONFIG['model_name']}")
        
        # Configurar Ollama LLM
        llm = Ollama(
            model=OLLAMA_CONFIG["model"],                 # llama3.2
            base_url=OLLAMA_CONFIG["base_url"],           # http://localhost:11434
            temperature=0.1,                              # Temperatura baja para respuestas consistentes
            request_timeout=120.0                         # Timeout de 2 minutos
        )
        print(f"✅ LLM configurado: {OLLAMA_CONFIG['model']} @ {OLLAMA_CONFIG['base_url']}")
        
        # Configurar Settings globales de LlamaIndex
        Settings.embed_model = embedding_model
        Settings.llm = llm
        print("✅ Settings globales configurados")
        
    except Exception as e:
        print(f"❌ Error configurando modelos: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 6: CARGAR ÍNDICE VECTORIAL EXISTENTE
    # ========================================
    print("6️⃣ CARGANDO ÍNDICE VECTORIAL...")
    print("-" * 40)
    
    try:
        # Configurar vector store para conectar a colección existente
        vector_store = MilvusVectorStore(
            host=MILVUS_CONFIG["host"],
            port=MILVUS_CONFIG["port"],
            user=MILVUS_CONFIG["user"],
            password=MILVUS_CONFIG["password"],
            collection_name=collection_name,             # Colección creada en test anterior
            dim=EMBEDDING_CONFIG["embedding_dim"]        # Dimensión debe coincidir
        )
        print(f"✅ Vector store conectado a colección: {collection_name}")
        
        # Cargar índice desde vector store existente
        index = VectorStoreIndex.from_vector_store(vector_store)
        print("✅ Índice vectorial cargado desde Milvus")
        
    except Exception as e:
        print(f"❌ Error cargando índice: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 7: CONFIGURAR MOTOR DE CONSULTAS
    # ========================================
    print("7️⃣ CONFIGURANDO MOTOR DE CONSULTAS...")
    print("-" * 40)
    
    try:
        # Configurar retriever para búsqueda vectorial
        retriever = VectorIndexRetriever(
            index=index,                                  # Índice vectorial cargado
            similarity_top_k=5                           # Recuperar top 5 documentos más similares
        )
        print("✅ Retriever configurado (top_k=5)")
        
        # Crear motor de consultas RAG
        query_engine = RetrieverQueryEngine(
            retriever=retriever                           # Usar el retriever configurado
        )
        print("✅ Motor de consultas RAG configurado")
        
    except Exception as e:
        print(f"❌ Error configurando motor de consultas: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 8: REALIZAR CONSULTAS DE PRUEBA
    # ========================================
    print("8️⃣ REALIZANDO CONSULTAS DE PRUEBA...")
    print("-" * 40)
    
    # Lista de preguntas de prueba
    test_questions = [
        "¿Cuál es el tema principal del documento?",
        "¿Qué es arquitectura de software?",
        "¿Cuáles son los conceptos más importantes mencionados?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        try:
            print(f"\n🔍 CONSULTA {i}: {question}")
            print("-" * 50)
            
            # Realizar consulta RAG
            print("⏳ Procesando consulta...")
            response = query_engine.query(question)
            
            # Mostrar respuesta
            answer = str(response)
            print(f"🤖 RESPUESTA:")
            print(f"{answer}")
            
            # Mostrar fuentes (si están disponibles)
            if hasattr(response, 'source_nodes') and response.source_nodes:
                print(f"\n📄 FUENTES CONSULTADAS:")
                for j, node in enumerate(response.source_nodes[:2], 1):  # Solo primeras 2
                    source_text = node.text[:150] + "..." if len(node.text) > 150 else node.text
                    print(f"  {j}. {source_text}")
            
            print(f"\n✅ Consulta {i} completada exitosamente")
            
        except Exception as e:
            print(f"❌ Error en consulta {i}: {e}")
            continue
    
    print()
    
    # ========================================
    # PASO 9: CONSULTA INTERACTIVA
    # ========================================
    print("9️⃣ MODO CONSULTA INTERACTIVA...")
    print("-" * 40)
    print("💡 Escribe tus preguntas (o 'salir' para terminar)")
    
    query_count = 0
    
    while True:
        try:
            # Solicitar pregunta al usuario
            user_question = input("\n❓ Tu pregunta: ").strip()
            
            # Verificar comandos especiales
            if user_question.lower() in ['salir', 'exit', 'quit', '']:
                break
            
            query_count += 1
            print(f"\n🔍 CONSULTA INTERACTIVA #{query_count}")
            print("-" * 30)
            
            # Realizar consulta
            print("⏳ Procesando...")
            response = query_engine.query(user_question)
            
            # Mostrar respuesta
            answer = str(response)
            print(f"\n🤖 RESPUESTA:")
            print(f"{answer}")
            
            # Mostrar metadatos
            if hasattr(response, 'source_nodes'):
                source_count = len(response.source_nodes) if response.source_nodes else 0
                print(f"\n📊 Metadatos: {source_count} fuentes consultadas")
            
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue
    
    print()
    
    # ========================================
    # RESUMEN FINAL
    # ========================================
    print("📋 RESUMEN DEL TEST DE CONSULTAS")
    print("=" * 50)
    print(f"✅ Conexión Milvus: {MILVUS_CONFIG['host']}:{MILVUS_CONFIG['port']}")
    print(f"✅ LLM: {OLLAMA_CONFIG['model']} @ {OLLAMA_CONFIG['base_url']}")
    print(f"✅ Embeddings: {EMBEDDING_CONFIG['model_name']}")
    print(f"✅ Colección: {collection_name}")
    print(f"✅ Consultas de prueba: {len(test_questions)} ejecutadas")
    print(f"✅ Consultas interactivas: {query_count} realizadas")
    print()
    print("🎉 ¡SISTEMA RAG COMPLETO FUNCIONANDO!")
    
    return True

if __name__ == "__main__":
    # Ejecutar test principal
    success = test_query_with_ollama()
    
    if success:
        print("\n🎉 ¡TEST DE CONSULTAS COMPLETADO EXITOSAMENTE!")
    else:
        print("\n❌ TEST FALLÓ - Revisar errores arriba")
        sys.exit(1)
