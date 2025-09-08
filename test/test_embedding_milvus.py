"""
🔬 TEST DE EMBEDDING E INDEXACIÓN CON MILVUS NORMAL
================================================================

Este script prueba todo el flujo de:
1. Conectar a Milvus normal (no lite)
2. Procesar PDFs con LlamaParse  
3. Generar embeddings multilingües
4. Almacenar en base de datos vectorizada Milvus

Ejecutar: python test/test_embedding_milvus.py
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

def test_embedding_and_indexing():
    """Función principal que prueba todo el flujo de embedding e indexación"""
    
    print("🚀 INICIANDO TEST DE EMBEDDING E INDEXACIÓN")
    print("=" * 70)
    print(f"⏰ Timestamp: {datetime.now()}")
    print()
    
    # ========================================
    # PASO 1: VERIFICAR CONFIGURACIÓN
    # ========================================
    print("1️⃣ VERIFICANDO CONFIGURACIÓN...")
    print("-" * 40)
    
    # Verificar que todas las variables de entorno estén disponibles
    required_vars = [
        'LLAMA_CLOUD_API_KEY',    # Para parsear PDFs
        'MILVUS_HOST',            # IP/host de Milvus
        'MILVUS_PORT',            # Puerto de Milvus (19530)
        'MILVUS_USER',            # Usuario de Milvus
        'MILVUS_PASSWORD',        # Password de Milvus
        'EMBEDDING_MODEL',        # Modelo para embeddings
        'OLLAMA_MODEL'            # Modelo LLM
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mostrar solo primeros caracteres para API keys por seguridad
            if 'KEY' in var:
                print(f"✅ {var}: {value[:10]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NO ENCONTRADA")
            return False
    
    print()
    
    # ========================================
    # PASO 2: IMPORTAR Y CONFIGURAR LIBRERÍAS
    # ========================================
    print("2️⃣ IMPORTANDO LIBRERÍAS...")
    print("-" * 40)
    
    try:
        # Importar LlamaParse para procesar PDFs
        from llama_parse import LlamaParse
        print("✅ LlamaParse importado correctamente")
        
        # Importar componentes de LlamaIndex para RAG
        from llama_index.core import Settings, VectorStoreIndex, Document
        from llama_index.core.node_parser import SentenceWindowNodeParser
        print("✅ LlamaIndex Core importado")
        
        # Importar embedding model de HuggingFace
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        print("✅ HuggingFace Embeddings importado")
        
        # Importar conector de Milvus
        from llama_index.vector_stores.milvus import MilvusVectorStore
        print("✅ Milvus VectorStore importado")
        
        # Importar cliente directo de Milvus para verificaciones
        from pymilvus import connections, Collection, utility
        print("✅ PyMilvus importado")
        
        # Importar configuración del proyecto
        from src.config import EMBEDDING_CONFIG, MILVUS_CONFIG
        print("✅ Configuración del proyecto importada")
        
    except ImportError as e:
        print(f"❌ Error importando librerías: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 3: CONECTAR A MILVUS NORMAL
    # ========================================
    print("3️⃣ CONECTANDO A MILVUS NORMAL...")
    print("-" * 40)
    
    try:
        # Desconectar cualquier conexión existente
        try:
            connections.disconnect("default")
            print("🔄 Desconectando conexiones previas")
        except:
            pass
        
        # Conectar a Milvus usando la configuración del .env
        connections.connect(
            alias="default",                          # Alias para la conexión
            host=MILVUS_CONFIG["host"],               # IP/host del servidor Milvus
            port=MILVUS_CONFIG["port"],               # Puerto (19530 por defecto)
            user=MILVUS_CONFIG["user"],               # Usuario (minioadmin por defecto)
            password=MILVUS_CONFIG["password"]        # Password
        )
        
        print(f"✅ Conectado a Milvus en {MILVUS_CONFIG['host']}:{MILVUS_CONFIG['port']}")
        
        # Verificar conexión listando colecciones existentes
        existing_collections = utility.list_collections()
        print(f"📋 Colecciones existentes: {existing_collections}")
        
    except Exception as e:
        print(f"❌ Error conectando a Milvus: {e}")
        print("💡 Verificar que Milvus esté ejecutándose y las credenciales sean correctas")
        return False
    
    print()
    
    # ========================================
    # PASO 4: CONFIGURAR MODELO DE EMBEDDINGS
    # ========================================
    print("4️⃣ CONFIGURANDO MODELO DE EMBEDDINGS...")
    print("-" * 40)
    
    try:
        # Crear instancia del modelo de embeddings multilingüe
        embedding_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_CONFIG["model_name"],    # Modelo multilingüe efederici/e5-base-multilingual-4096
            max_length=512                                # Longitud máxima de tokens
        )
        print(f"✅ Modelo configurado: {EMBEDDING_CONFIG['model_name']}")
        
        # Probar el modelo con texto de ejemplo
        test_text = "Este es un texto de prueba para verificar embeddings"
        test_embedding = embedding_model.get_text_embedding(test_text)
        print(f"✅ Test de embedding exitoso - Dimensión: {len(test_embedding)}")
        
        # Configurar Settings globales de LlamaIndex
        Settings.embed_model = embedding_model
        print("✅ Settings de LlamaIndex configurados")
        
    except Exception as e:
        print(f"❌ Error configurando embeddings: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 5: CONFIGURAR PARSER DE PDFs
    # ========================================
    print("5️⃣ CONFIGURANDO PARSER DE PDFs...")
    print("-" * 40)
    
    try:
        # Crear instancia de LlamaParse para procesar PDFs
        parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),    # API key de LlamaCloud
            result_type="markdown",                       # Formato de salida
            verbose=True,                                 # Mostrar progreso
            show_progress=True                            # Barra de progreso
        )
        print("✅ LlamaParse configurado correctamente")
        
        # Configurar parser de nodos para chunking
        node_parser = SentenceWindowNodeParser(
            window_size=3,                               # Ventana de 3 oraciones
            window_metadata_key="window",               # Key para metadata de ventana
            original_text_metadata_key="original_text"  # Key para texto original
        )
        Settings.node_parser = node_parser
        print("✅ Node parser configurado (ventana de 3 oraciones)")
        
    except Exception as e:
        print(f"❌ Error configurando parser: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 6: PROCESAR DOCUMENTO PDF
    # ========================================
    print("6️⃣ PROCESANDO DOCUMENTO PDF...")
    print("-" * 40)
    
    # Buscar un PDF en la carpeta pdfs
    pdf_path = "pdfs/Introduccion-a-la-arquitectura-de-software-v1.0.2.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF no encontrado: {pdf_path}")
        print("💡 Coloca un PDF en la carpeta pdfs/ para probar")
        return False
    
    try:
        print(f"📄 Procesando: {pdf_path}")
        
        # Usar LlamaParse para extraer contenido del PDF
        documents = parser.load_data(pdf_path)
        print(f"✅ Documentos extraídos: {len(documents)}")
        
        if not documents:
            print("❌ No se pudo extraer contenido del PDF")
            return False
        
        # Agregar metadata útil a cada documento
        for i, doc in enumerate(documents):
            doc.metadata.update({
                "source_file": os.path.basename(pdf_path),     # Nombre del archivo
                "indexed_at": datetime.now().isoformat(),      # Timestamp de indexación
                "file_path": pdf_path,                         # Ruta completa
                "document_index": i,                           # Índice del documento
                "total_documents": len(documents)              # Total de documentos
            })
        
        # Mostrar información del primer documento
        first_doc = documents[0]
        print(f"📝 Primer documento - Longitud: {len(str(first_doc))} caracteres")
        print(f"📝 Preview: {str(first_doc)[:200]}...")
        
    except Exception as e:
        print(f"❌ Error procesando PDF: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 7: CONFIGURAR VECTOR STORE MILVUS
    # ========================================
    print("7️⃣ CONFIGURANDO VECTOR STORE...")
    print("-" * 40)
    
    try:
        collection_name = "test_arquitectura_completa"
        
        # Crear vector store para Milvus normal (no lite)
        vector_store = MilvusVectorStore(
            host=MILVUS_CONFIG["host"],                  # Host de Milvus
            port=MILVUS_CONFIG["port"],                  # Puerto de Milvus
            user=MILVUS_CONFIG["user"],                  # Usuario
            password=MILVUS_CONFIG["password"],          # Password
            collection_name=collection_name,             # Nombre de la colección
            dim=EMBEDDING_CONFIG["embedding_dim"],       # Dimensión de embeddings (768)
            overwrite=True                               # Sobrescribir si existe
        )
        print(f"✅ Vector store configurado para colección: {collection_name}")
        print(f"📐 Dimensión de embeddings: {EMBEDDING_CONFIG['embedding_dim']}")
        
    except Exception as e:
        print(f"❌ Error configurando vector store: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 8: CREAR ÍNDICE VECTORIAL
    # ========================================
    print("8️⃣ CREANDO ÍNDICE VECTORIAL...")
    print("-" * 40)
    
    try:
        print("🔄 Iniciando proceso de indexación...")
        
        # Usar solo primeros 5 documentos para prueba (más rápido)
        test_documents = documents[:5]
        print(f"📊 Procesando {len(test_documents)} documentos de prueba")
        
        # Crear índice vectorial usando LlamaIndex
        index = VectorStoreIndex.from_documents(
            test_documents,                              # Documentos a indexar
            vector_store=vector_store,                   # Vector store de Milvus
            show_progress=True                           # Mostrar barra de progreso
        )
        
        print("✅ Índice vectorial creado exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando índice: {e}")
        return False
    
    print()
    
    # ========================================
    # PASO 9: VERIFICAR INDEXACIÓN
    # ========================================
    print("9️⃣ VERIFICANDO INDEXACIÓN...")
    print("-" * 40)
    
    try:
        # Verificar que la colección fue creada
        if utility.has_collection(collection_name):
            collection = Collection(collection_name)
            collection.load()                            # Cargar colección en memoria
            
            # Obtener estadísticas
            doc_count = collection.num_entities
            print(f"✅ Colección creada: {collection_name}")
            print(f"📊 Documentos almacenados: {doc_count}")
            
            # Verificar esquema
            schema = collection.schema
            fields = [field.name for field in schema.fields]
            print(f"🏗️ Campos en la colección: {fields}")
            
            if doc_count > 0:
                print("🎉 ¡INDEXACIÓN COMPLETADA EXITOSAMENTE!")
            else:
                print("⚠️ Colección creada pero sin documentos")
                
        else:
            print(f"❌ Colección {collection_name} no fue creada")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando indexación: {e}")
        return False
    
    print()
    
    # ========================================
    # RESUMEN FINAL
    # ========================================
    print("📋 RESUMEN DEL TEST")
    print("=" * 50)
    print(f"✅ Conexión a Milvus: {MILVUS_CONFIG['host']}:{MILVUS_CONFIG['port']}")
    print(f"✅ PDF procesado: {os.path.basename(pdf_path)}")
    print(f"✅ Documentos indexados: {doc_count}")
    print(f"✅ Colección creada: {collection_name}")
    print(f"✅ Modelo embedding: {EMBEDDING_CONFIG['model_name']}")
    print()
    print("🎯 SIGUIENTE PASO: Ejecutar test_query_ollama.py para probar consultas")
    
    return True

if __name__ == "__main__":
    # Ejecutar test principal
    success = test_embedding_and_indexing()
    
    if success:
        print("\n🎉 ¡TEST DE EMBEDDING COMPLETADO EXITOSAMENTE!")
    else:
        print("\n❌ TEST FALLÓ - Revisar errores arriba")
        sys.exit(1)
