# 🚀 Sistema RAG Lumina con Milvus Docker y Ollama

## Archivos Principales

- **`index_documents.py`**: Indexa documentos usando LlamaParse, grafo y Milvus Docker
- **`query_system.py`**: Sistema de consultas con Ollama Llama3.2 y contexto de grafo
- **`run_help.sh`**: Script de ayuda con comandos y verificaciones

## Uso Rápido

### 1. Indexar Documentos
```bash
# Indexar todos los PDFs de la carpeta
python index_documents.py

# Indexar archivo específico
python index_documents.py pdfs/documento.pdf
```

### 2. Hacer Consultas
```bash
# Modo interactivo
python query_system.py --interactive

# Consulta específica
python query_system.py --query "¿Qué dice sobre arquitectura?"
```

### 3. Ver Ayuda
```bash
./run_help.sh
```

## Características

✅ **LlamaParse**: Convierte PDFs e imágenes a texto estructurado  
✅ **Grafo de Documentos**: Preserva estructura y contexto entre chunks  
✅ **Milvus Docker**: Base de datos vectorial externa (no Milvus Lite)  
✅ **Ollama Llama3.2**: LLM local para consultas  
✅ **Búsqueda Híbrida**: Combina vectores + navegación de grafo  

## Requisitos Previos

1. **Milvus Docker ejecutándose**
2. **Ollama con modelo llama3.2**
3. **API Key de LlamaParse en .env**

## Verificación del Sistema

```bash
# Verificar Milvus
docker ps | grep milvus

# Verificar Ollama
curl http://localhost:11434/api/tags

# Verificar modelo
ollama list | grep llama3.2
```

## Variables de Entorno (.env)

```env
LLAMA_CLOUD_API_KEY=tu_api_key_aqui
MILVUS_HOST=localhost
MILVUS_PORT=19530
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Flujo de Trabajo

1. **Indexación**: `index_documents.py` procesa PDFs → Crea grafo → Indexa en Milvus
2. **Consulta**: `query_system.py` busca en Milvus → Enriquece con grafo → Responde con Ollama

## Archivos Generados

- **`document_graph.pkl`**: Grafo serializado para consultas
- **Colección Milvus**: `lumina_rag_documents` en tu Milvus Docker

## Modo Interactivo

En modo interactivo puedes usar comandos especiales:
- `stats`: Ver estadísticas del sistema
- `help`: Ver ayuda
- `clear`: Limpiar pantalla
- `quit`: Salir