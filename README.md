# Configuración Centralizada para LuminaMO_RAG

Este módulo provee una configuración centralizada para todo el sistema RAG. Todos los parámetros ajustables están definidos en el archivo `.env`.

## Estructura

La configuración está organizada en los siguientes grupos y todos los valores DEBEN ser definidos en el archivo `.env`:

### CHUNKING_CONFIG

Controla el comportamiento del chunking (fragmentación) de documentos:

- `chunk_size`: Tamaño de cada fragmento en tokens (Variable de entorno: `CHUNK_SIZE`, valor por defecto: 2000)
- `chunk_overlap`: Solapamiento entre fragmentos en tokens (Variable de entorno: `CHUNK_OVERLAP`, valor por defecto: 100)
- `chunk_window_size`: Número de oraciones por ventana para el SentenceWindowNodeParser (Variable de entorno: `CHUNK_WINDOW_SIZE`, valor por defecto: 3)

### EMBEDDING_CONFIG

Configuración relacionada con los modelos de embedding:

- `embedding_dim`: Dimensión del vector de embedding (Variable de entorno: `EMBEDDING_DIM`, valor por defecto: 768)
- `model_name`: Modelo de embedding a utilizar (Variable de entorno: `EMBEDDING_MODEL`, valor por defecto: "efederici/e5-base-multilingual-4096")

### MILVUS_CONFIG

Configuración para la conexión a Milvus:

- `host`: Host de Milvus (Variable de entorno: `MILVUS_HOST`, valor por defecto: "localhost")
- `port`: Puerto de Milvus (Variable de entorno: `MILVUS_PORT`, valor por defecto: "19530")
- `user`: Usuario de Milvus (Variable de entorno: `MILVUS_USER`, valor por defecto: "minioadmin")
- `password`: Contraseña de Milvus (Variable de entorno: `MILVUS_PASSWORD`, valor por defecto: "minioadmin")

### OLLAMA_CONFIG

Configuración para la conexión a Ollama:

- `model`: Modelo a utilizar en Ollama (Variable de entorno: `OLLAMA_MODEL`, valor por defecto: "llama3.2")
- `base_url`: URL base para conectar con Ollama (Variable de entorno: `OLLAMA_BASE_URL`, valor por defecto: "http://localhost:11435")

### PATH_CONFIG

Configuración de rutas:

- `pdf_directory`: Directorio donde se encuentran los archivos PDF (Variable de entorno: `PDF_DIRECTORY`, valor por defecto: "pdfs")

## Uso

Para utilizar la configuración en cualquier módulo, simplemente importa los objetos de configuración necesarios:

```python
from src.config import CHUNKING_CONFIG, EMBEDDING_CONFIG, MILVUS_CONFIG, OLLAMA_CONFIG, PATH_CONFIG

# Usar la configuración
chunk_size = CHUNKING_CONFIG["chunk_size"]
model_name = EMBEDDING_CONFIG["model_name"]
```

## Modificación de la Configuración

Para configurar el sistema:

**Usando el archivo .env**: Define todas las variables necesarias en el archivo `.env`.
Ejemplo de archivo `.env`:
```
CHUNK_SIZE=3000
CHUNK_OVERLAP=100
CHUNK_WINDOW_SIZE=3
EMBEDDING_DIM=768
EMBEDDING_MODEL=efederici/e5-base-multilingual-4096
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=minioadmin
MILVUS_PASSWORD=minioadmin
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11435
PDF_DIRECTORY=pdfs
```

**IMPORTANTE**: Todas las variables deben estar definidas en el archivo `.env` para que el sistema funcione correctamente.
