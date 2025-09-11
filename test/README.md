# 🔬 Tests del Sistema RAG Jerárquico

Esta carpeta contiene tests para verificar la **nueva arquitectura jerárquica** del sistema RAG con **Milvus** y **Ollama/Llama3.2**.

## 📁 Archivos de Test Actuales

### 1. `test_refactored_architecture.py` - Test Arquitectura Jerárquica
**Propósito:** Probar la nueva arquitectura jerárquica completa
```bash
python test/test_refactored_architecture.py
```

**Qué verifica:**
- ✅ **Grafos Jerárquicos** → Árboles por documento con nodos raíz
- ✅ **Meta-Grafo** → Conexiones entre documentos
- ✅ **PageRank Especializado** → Múltiples estrategias de análisis
- ✅ **Indexación Milvus** → Schema jerárquico con campos especializados
- ✅ **Consultas Avanzadas** → Contexto enriquecido y estrategias múltiples

### 2. `hybrid_retriever.py` - Sistema de Recuperación Híbrido
**Propósito:** Implementación avanzada de recuperación
```bash
python test/hybrid_retriever.py
```

**Características:**
- 🔍 **Recuperación Semántica** → Búsqueda por similitud vectorial
- 📊 **Ranking Jerárquico** → Priorización basada en importancia del grafo
- 🌐 **Contexto Multi-documento** → Información cruzada entre documentos

### 3. `scalability_analysis.py` - Análisis de Escalabilidad
**Propósito:** Evaluar rendimiento del sistema jerárquico
```bash
python test/scalability_analysis.py
```

**Métricas evaluadas:**
- ⚡ **Tiempo de indexación** → Performance con múltiples documentos
- 🧠 **Uso de memoria** → Eficiencia de grafos jerárquicos
- 🔄 **Velocidad de consulta** → Respuesta con diferentes estrategias

## ⚙️ Configuración para Nueva Arquitectura

### Variables en `.env`
```bash
# Configuración básica
CHUNK_SIZE=2000
CHUNK_OVERLAP=100
CHUNK_WINDOW_SIZE=3

# Embeddings multilingües
EMBEDDING_MODEL=efederici/e5-base-multilingual-4096
EMBEDDING_DIM=768

# Milvus (normal)
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=minioadmin
MILVUS_PASSWORD=minioadmin

# Ollama local
OLLAMA_BASE_URL=http://localhost:11435
OLLAMA_MODEL=llama3.2

# Rutas
PDF_DIRECTORY=pdfs
```

### Servicios Requeridos

#### 1. **Milvus Standalone**
```bash
# En directorio Lumina_Milvus
docker-compose up -d
```

#### 2. **Ollama con Llama3.2**
```bash
# En directorio LuminaMO_Model_IA  
docker-compose up -d
```

## 🚀 Flujo de Testing Jerárquico

### Opción A: Test Completo de Arquitectura
```bash
# Verificar nueva arquitectura jerárquica
python test/test_refactored_architecture.py
```

### Opción B: Análisis Individual
```bash
# 1. Evaluar escalabilidad
python test/scalability_analysis.py

# 2. Probar recuperación híbrida
python test/hybrid_retriever.py
```

### Opción C: Verificación del Sistema
```bash
# Verificar que todo esté funcionando
python check_system.py
```

## 📊 Arquitectura Jerárquica Explicada

### 🌳 Estructura de Grafos por Documento

```python
# Cada documento forma un árbol binario balanceado
Document_1/
├── Root_Node (nivel 0)
│   ├── Branch_A (nivel 1)
│   │   ├── Chunk_1 (nivel 2)
│   │   └── Chunk_2 (nivel 2)
│   └── Branch_B (nivel 1)
│       ├── Chunk_3 (nivel 2)
│       └── Chunk_4 (nivel 2)

# Las raíces se conectan en meta-grafo
Root_Doc1 ←→ Root_Doc2 ←→ Root_Doc3
```

### 🔍 Estrategias de Consulta Jerárquica

```python
# 1. MIXED: Combina todos los enfoques
strategy = "mixed"
results = hierarchical_query(query, strategy=strategy)

# 2. ROOTS_FIRST: Prioriza nodos raíz
strategy = "roots_first" 
results = hierarchical_query(query, strategy=strategy)

# 3. WITHIN_DOCS: Búsqueda dentro de documentos
strategy = "within_docs"
results = hierarchical_query(query, strategy=strategy)

# 4. META_ONLY: Solo conexiones meta-grafo  
strategy = "meta_only"
results = hierarchical_query(query, strategy=strategy)
```

### � Schema Milvus Jerárquico

```python
# Campos especializados para arquitectura jerárquica
schema = {
    "chunk_id": "string",           # ID único del chunk
    "content": "string",            # Contenido del chunk
    "embedding": "float_vector",    # Vector 768-dim
    
    # Campos jerárquicos nuevos
    "document_name": "string",      # Documento origen
    "is_root": "bool",             # ¿Es nodo raíz?
    "tree_level": "int",           # Nivel en el árbol
    "parent_chunk": "string",      # ID del chunk padre
    "hierarchical_importance": "float"  # Score PageRank jerárquico
}
```

## 🎯 Migración desde Arquitectura Anterior

### Scripts Eliminados (Legacy):
- ❌ `manual_index_legacy.py` (era `manual_index.py`)
- ❌ `simple_query_legacy.py` (era `simple_query.py`)  
- ❌ `example.py` (ejemplo obsoleto)
- ❌ `test_complete_flow.py` (flujo no jerárquico)
- ❌ `test_embedding_milvus.py` (embedding simple)
- ❌ `test_query_ollama.py` (consultas simples)
- ❌ `test_chunking.py` (chunking no jerárquico)
- ❌ `test_graph.py` (grafo simple)
- ❌ `test_llama_parse.py` (parsing básico)

### Scripts Actuales (Jerárquicos):
- ✅ `index.py` (indexador jerárquico principal)
- ✅ `query.py` (sistema de consultas avanzado)
- ✅ `utils.py` (herramientas de gestión)
- ✅ `migrate_graph.py` (migración automática)
- ✅ `check_system.py` (verificación completa)

## �️ Solución de Problemas Jerárquicos

### Error: "Grafo jerárquico no encontrado"
```bash
# Migrar desde grafo simple
python migrate_graph.py
```

### Error: "Schema jerárquico no compatible"
```bash
# Recrear colección con nuevo schema
python index.py
```

### Error: "Estrategia jerárquica no reconocida"
```bash
# Usar estrategias válidas: mixed, roots_first, within_docs, meta_only
python query.py
```

## 📈 Resultados Esperados de la Nueva Arquitectura

### test_refactored_architecture.py exitoso:
```
✅ Grafo jerárquico cargado: 6 documentos, 120 chunks
✅ Meta-grafo creado: 117 conexiones meta-documento
✅ PageRank jerárquico calculado: estrategias disponibles
✅ Schema Milvus jerárquico: 8 campos especializados
✅ Indexación jerárquica: 120 chunks con información de árbol
✅ Consultas avanzadas: 4 estrategias funcionando
🎉 ¡ARQUITECTURA JERÁRQUICA COMPLETAMENTE FUNCIONAL!
```

### Ventajas de la Nueva Arquitectura:
- 🌳 **Organización mejorada**: Árboles por documento
- 🔍 **Consultas inteligentes**: Múltiples estrategias especializadas  
- 📊 **Escalabilidad**: Meta-grafo para análisis cruzado
- ⚡ **Performance**: PageRank jerárquico optimizado
- 🧠 **Contexto rico**: Información estructural en respuestas

---

🌟 **Nueva arquitectura jerárquica para análisis de documentos de siguiente nivel**
