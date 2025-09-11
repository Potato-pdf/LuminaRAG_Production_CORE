# 🌟 LuminaMO_RAG - Sistema RAG Jerárquico Avanzado

Sistema de Recuperación Aumentada Generativa (RAG) con arquitectura jerárquica de grafos, embeddings multilingües y análisis de grafos avanzado.

## 🏗️ Arquitectura

### 🌳 Grafos Jerárquicos
- **Grafos por Documento**: Cada documento forma un árbol balanceado binario con nodos raíz
- **Meta-Grafo**: Las raíces de documentos se conectan para análisis cruzado
- **Análisis PageRank**: Estrategias especializadas (mixed, roots_first, within_docs, meta_only)
- **Migración Automática**: Convierte grafos simples a jerárquicos sin pérdida de datos

### 🔧 Componentes Principales
- **index.py**: Indexador principal con esquema Milvus jerárquico
- **query.py**: Sistema de consultas avanzado con múltiples estrategias
- **utils.py**: Herramientas de gestión y comparación de grafos
- **migrate_graph.py**: Migración de arquitecturas legacy

## 🚀 Inicio Rápido

### 1. Configuración del Entorno
```bash
# Instalar dependencias
pip install -r requirements.txt

# Tu archivo .env ya está configurado correctamente con:
# - LLAMA_CLOUD_API_KEY para LlamaParse
# - OLLAMA_MODEL=llama3.2:latest
# - MILVUS configurado en localhost:19530
# - Embeddings multilingües configurados
```

### 2. Iniciar Servicios
```bash
# Milvus (en directorio Lumina_Milvus)
docker-compose up -d

# Ollama (en directorio LuminaMO_Model_IA)
docker-compose up -d
```

### 3. Indexar Documentos
```bash
# Indexación jerárquica principal
python3 index.py

# Ver estadísticas del proceso
python3 utils.py
```

### 4. Consultar Sistema
```bash
# Sistema interactivo avanzado
python3 query.py

# Seleccionar estrategia de búsqueda:
# - mixed: Combina todos los enfoques
# - roots_first: Prioriza nodos raíz
# - within_docs: Búsqueda dentro de documentos
# - meta_only: Solo conexiones meta-grafo
```

## 📁 Estructura del Proyecto

```
LuminaMO_RAG/
├── 📄 index.py              # Indexador principal jerárquico
├── 🔍 query.py              # Sistema de consultas avanzado
├── 🔧 utils.py              # Utilidades de gestión
├── 🔄 migrate_graph.py      # Migración de grafos
├── 📚 src/
│   ├── 🗂️ document_graph/
│   │   ├── hierarchical_graph.py     # Grafo jerárquico principal
│   │   ├── simple_graph.py           # Grafo simple base
│   │   ├── core/
│   │   │   ├── hierarchical_analyzer.py  # Análisis PageRank jerárquico
│   │   │   ├── graph_analyzer.py         # Análisis base
│   │   │   └── graph_manager.py          # Gestión de grafos
│   │   └── utils/
│   │       ├── hierarchical_graph_builder.py  # Constructor jerárquico
│   │       └── graph_builder.py               # Constructor base
│   ├── 🔗 embedding/          # Modelos de embedding
│   ├── 🤖 model_ai/           # Integración LLM
│   ├── 🗄️ db_milvus/          # Conexión y esquemas Milvus
│   └── ⚙️ config/             # Configuración centralizada
└── 📖 test/                   # Scripts de prueba y validación
```

## 🎯 Características Avanzadas

### 🌳 Arquitectura Jerárquica
- **Árboles por Documento**: Cada documento se organiza como árbol binario balanceado
- **Nodos Raíz**: Representan el contexto general del documento
- **Niveles Jerárquicos**: Profundidad automática basada en contenido
- **Conexiones Meta**: Enlaces inteligentes entre documentos

### 📊 Análisis de Grafos
- **PageRank Especializado**: Múltiples estrategias según el caso de uso
- **Importancia Jerárquica**: Scores que consideran posición en el árbol
- **Contexto Enriquecido**: Combina información jerárquica y semántica

### 🔍 Búsqueda Inteligente
- **Estrategias Múltiples**: Adaptadas a diferentes tipos de consultas
- **Contexto Rico**: Incluye información jerárquica en respuestas
- **Modo Interactivo**: Interfaz amigable para experimentación

## ⚙️ Configuración

La configuración está organizada en los siguientes grupos y todos los valores DEBEN ser definidos en el archivo `.env`:

### 🔧 CHUNKING_CONFIG

Controla el comportamiento del chunking (fragmentación) de documentos:

- `chunk_size`: Tamaño de cada fragmento en tokens (Variable de entorno: `CHUNK_SIZE`, valor por defecto: 2000)
- `chunk_overlap`: Solapamiento entre fragmentos en tokens (Variable de entorno: `CHUNK_OVERLAP`, valor por defecto: 100)
- `chunk_window_size`: Número de oraciones por ventana para el SentenceWindowNodeParser (Variable de entorno: `CHUNK_WINDOW_SIZE`, valor por defecto: 3)

### 🤖 EMBEDDING_CONFIG

Configuración relacionada con los modelos de embedding:

- `embedding_dim`: Dimensión del vector de embedding (Variable de entorno: `EMBEDDING_DIM`, valor por defecto: 768)
- `model_name`: Modelo de embedding a utilizar (Variable de entorno: `EMBEDDING_MODEL`, valor por defecto: "efederici/e5-base-multilingual-4096")

### 🗄️ MILVUS_CONFIG

Configuración para la conexión a Milvus:

- `host`: Host de Milvus (Variable de entorno: `MILVUS_HOST`, valor por defecto: "localhost")
- `port`: Puerto de Milvus (Variable de entorno: `MILVUS_PORT`, valor por defecto: "19530")
- `user`: Usuario de Milvus (Variable de entorno: `MILVUS_USER`, valor por defecto: "minioadmin")
- `password`: Contraseña de Milvus (Variable de entorno: `MILVUS_PASSWORD`, valor por defecto: "minioadmin")

### 🦙 OLLAMA_CONFIG

Configuración para la conexión a Ollama:

- `model`: Modelo a utilizar en Ollama (Variable de entorno: `OLLAMA_MODEL`, valor por defecto: "llama3.2")
- `base_url`: URL base para conectar con Ollama (Variable de entorno: `OLLAMA_BASE_URL`, valor por defecto: "http://localhost:11435")

### 📁 PATH_CONFIG

Configuración de rutas:

- `pdf_directory`: Directorio donde se encuentran los archivos PDF (Variable de entorno: `PDF_DIRECTORY`, valor por defecto: "pdfs")

## 💻 Uso Programático

Para utilizar la configuración en cualquier módulo, simplemente importa los objetos de configuración necesarios:

```python
from src.config import CHUNKING_CONFIG, EMBEDDING_CONFIG, MILVUS_CONFIG, OLLAMA_CONFIG, PATH_CONFIG

# Usar la configuración
chunk_size = CHUNKING_CONFIG["chunk_size"]
model_name = EMBEDDING_CONFIG["model_name"]
```

## 🔧 Modificación de la Configuración

Para configurar el sistema:

**Usando el archivo .env**: Tu archivo `.env` ya está configurado correctamente con todas las variables necesarias:

```bash
# Tu configuración actual (.env)
LLAMA_CLOUD_API_KEY=llx-xxx (configurado)
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11435
MILVUS_HOST=localhost
MILVUS_PORT=19530
EMBEDDING_MODEL=efederici/e5-base-multilingual-4096
# ... y todas las demás variables necesarias
```

**IMPORTANTE**: Todas las variables deben estar definidas en el archivo `.env` para que el sistema funcione correctamente.

## 🧪 Testing y Validación

```bash
# Ejecutar pruebas completas
python3 test/test_complete_flow.py

# Probar arquitectura jerárquica
python3 test/test_refactored_architecture.py

# Validar migración
python3 migrate_graph.py

# Utilidades de gestión
python3 utils.py
```

## 🚨 Migración desde Versiones Anteriores

Si tienes grafos simples existentes:

```bash
# Migración automática
python3 migrate_graph.py

# Verificar resultado
python3 utils.py
# Seleccionar opción 1: Comparar grafos
```

## 📈 Monitoreo y Estadísticas

```bash
# Ver estadísticas detalladas
python3 utils.py
# Seleccionar opción 4: Estadísticas detalladas

# Inspeccionar grafo específico
python3 utils.py  
# Seleccionar opción 5: Inspeccionar grafo específico
```

## 🛠️ Arquitecturas Disponibles

### 🌳 Jerárquica (Recomendada)
- **Uso**: `python3 index.py` y `python3 query.py`
- **Ventajas**: Mejor organización, análisis avanzado, escalabilidad
- **Casos de uso**: Múltiples documentos, análisis detallado

### 📝 Simple (Legacy)
- **Uso**: `python3 manual_index_legacy.py` y `python3 simple_query_legacy.py`
- **Ventajas**: Simplicidad, compatibilidad
- **Casos de uso**: Documentos únicos, pruebas rápidas

---

🌟 **Desarrollado para análisis de documentos inteligente con arquitectura jerárquica avanzada**
