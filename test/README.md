# 🔬 Tests del Sistema RAG con Milvus Normal

Esta carpeta contiene tests completos para verificar todo el flujo del sistema RAG usando **Milvus normal** (no lite) y **Ollama/Llama3.2**.

## 📁 Archivos de Test

### 1. `test_embedding_milvus.py` - Test de Indexación
**Propósito:** Probar proceso completo de embedding e indexación
```bash
python test/test_embedding_milvus.py
```

**Qué hace cada parte:**
- ✅ **Verificar configuración** → Lee variables de .env
- ✅ **Conectar a Milvus normal** → Usa host/port/user/password
- ✅ **Configurar embeddings** → Modelo multilingüe HuggingFace
- ✅ **Procesar PDF** → LlamaParse extrae contenido
- ✅ **Crear índice vectorial** → Almacena en Milvus
- ✅ **Verificar almacenamiento** → Confirma documentos guardados

### 2. `test_query_ollama.py` - Test de Consultas
**Propósito:** Probar consultas RAG con Ollama/Llama3.2
```bash
python test/test_query_ollama.py
```

**Qué hace cada parte:**
- ✅ **Verificar Ollama** → Conecta a localhost:11434
- ✅ **Cargar índice** → Lee datos de Milvus
- ✅ **Configurar RAG** → Motor de consultas + LLM
- ✅ **Consultas automáticas** → 3 preguntas predefinidas
- ✅ **Modo interactivo** → Pregunta lo que quieras

### 3. `test_complete_flow.py` - Test End-to-End
**Propósito:** Probar flujo completo desde PDF hasta consultas
```bash
python test/test_complete_flow.py
```

**Qué hace cada parte:**
- ✅ **Verificación inicial** → Archivos y configuración
- ✅ **Fase 1: Indexación** → PDF → Embeddings → Milvus
- ✅ **Fase 2: Consultas** → Milvus → LLM → Respuestas
- ✅ **Verificación final** → Todo el sistema funcionando

## ⚙️ Configuración Necesaria

### Variables en `.env`
```bash
# Obligatorias para tests
LLAMA_CLOUD_API_KEY=llx-xxx
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=minioadmin
MILVUS_PASSWORD=minioadmin
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
EMBEDDING_MODEL=efederici/e5-base-multilingual-4096
EMBEDDING_DIM=768
```

### Servicios Requeridos

#### 1. **Milvus Standalone**
```bash
# Instalar con Docker
docker run -d --name milvus-standalone \
  -p 19530:19530 \
  -v $(pwd)/milvus:/var/lib/milvus \
  milvusdb/milvus:latest standalone
```

#### 2. **Ollama con Llama3.2**
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama3.2

# Ejecutar servidor
ollama serve
```

## 🚀 Cómo Usar los Tests

### Opción A: Test Individual
```bash
# 1. Solo indexación
python test/test_embedding_milvus.py

# 2. Solo consultas (después del paso 1)
python test/test_query_ollama.py
```

### Opción B: Test Completo
```bash
# Todo el flujo de una vez
python test/test_complete_flow.py
```

### Opción C: Verificar servicios
```bash
# Verificar Milvus
curl http://localhost:19530/health

# Verificar Ollama
curl http://localhost:11434/api/tags
```

## 📊 Explicación Técnica Detallada

### 🔄 Flujo de Embedding (test_embedding_milvus.py)

```python
# 1. CONECTAR A MILVUS NORMAL
connections.connect(
    host="localhost",      # ← Tu servidor Milvus
    port=19530,           # ← Puerto estándar Milvus
    user="minioadmin",    # ← Usuario por defecto
    password="minioadmin" # ← Password por defecto
)

# 2. CONFIGURAR EMBEDDINGS
embedding_model = HuggingFaceEmbedding(
    model_name="efederici/e5-base-multilingual-4096",  # ← Modelo multilingüe
    max_length=512                                     # ← Tokens máximos
)

# 3. PROCESAR PDF
parser = LlamaParse(
    api_key="llx-xxx",    # ← Tu API key de LlamaCloud
    result_type="markdown" # ← Formato de salida
)
documents = parser.load_data("archivo.pdf")  # ← Extraer contenido

# 4. CREAR VECTOR STORE
vector_store = MilvusVectorStore(
    host="localhost",     # ← Mismo host que conexión
    port=19530,          # ← Mismo puerto
    collection_name="mi_coleccion",  # ← Nombre único
    dim=768              # ← Dimensión del modelo embedding
)

# 5. INDEXAR DOCUMENTOS
index = VectorStoreIndex.from_documents(
    documents,           # ← Documentos procesados
    vector_store=vector_store  # ← Destino en Milvus
)
```

### 🔍 Flujo de Consultas (test_query_ollama.py)

```python
# 1. CONFIGURAR LLM
llm = Ollama(
    model="llama3.2",                    # ← Modelo local descargado
    base_url="http://localhost:11434",   # ← Servidor Ollama
    temperature=0.1                      # ← Respuestas consistentes
)

# 2. CARGAR ÍNDICE EXISTENTE
vector_store = MilvusVectorStore(
    host="localhost", port=19530,        # ← Conectar a Milvus
    collection_name="mi_coleccion"       # ← Colección con datos
)
index = VectorStoreIndex.from_vector_store(vector_store)

# 3. CREAR MOTOR DE CONSULTAS
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=5   # ← Recuperar 5 documentos más similares
)
query_engine = RetrieverQueryEngine(retriever=retriever)

# 4. REALIZAR CONSULTA RAG
response = query_engine.query("¿Cuál es el tema principal?")
# Flujo interno:
# Tu pregunta → Embedding → Búsqueda en Milvus → 
# Documentos relevantes → Contexto + Pregunta → LLM → Respuesta
```

## 🎯 Puntos Clave de Configuración

### Para Cambiar a Tu Servidor Milvus:
```python
# En todos los tests, cambiar:
MILVUS_HOST = "tu-servidor-milvus.com"  # ← Tu IP/dominio
MILVUS_PORT = 19530                     # ← Puerto (19530 estándar)
MILVUS_USER = "tu-usuario"              # ← Tu usuario
MILVUS_PASSWORD = "tu-password"         # ← Tu contraseña
```

### Para Usar Otro Modelo LLM:
```python
# En test_query_ollama.py y test_complete_flow.py:
OLLAMA_MODEL = "llama3.1"               # ← Cambiar modelo
# Ejecutar: ollama pull llama3.1
```

### Para Otro Modelo de Embeddings:
```python
# Cambiar en .env:
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # ← Ajustar dimensión del nuevo modelo
```

## 🔧 Solución de Problemas

### Error: "Cannot connect to Milvus"
```bash
# Verificar Milvus
docker ps | grep milvus
curl http://localhost:19530/health
```

### Error: "Ollama not responding"
```bash
# Verificar Ollama
ollama list
curl http://localhost:11434/api/tags
```

### Error: "LlamaParse API key"
```bash
# Verificar API key en .env
echo $LLAMA_CLOUD_API_KEY
```

### Error: "Collection not found"
```bash
# Ejecutar indexación primero
python test/test_embedding_milvus.py
```

## 📈 Resultados Esperados

### test_embedding_milvus.py exitoso:
```
✅ Conectado a Milvus en localhost:19530
✅ Documentos extraídos: 549
✅ Índice vectorial creado exitosamente
✅ Documentos almacenados: 10
🎉 ¡INDEXACIÓN COMPLETADA EXITOSAMENTE!
```

### test_query_ollama.py exitoso:
```
✅ Ollama está ejecutándose en http://localhost:11434
✅ Modelo llama3.2 está disponible
✅ Colección encontrada: test_arquitectura_completa (10 documentos)
🤖 RESPUESTA: El documento trata sobre arquitectura de software...
🎉 ¡SISTEMA RAG COMPLETO FUNCIONANDO!
```

¡Estos tests te darán total confianza de que el sistema funciona antes de cambiar de computadora!
