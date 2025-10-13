# 🌐 API REST - Lumina RAG

API REST para exponer el sistema de consultas RAG sin modificar la lógica existente del modelo, grafo ni arquitectura.

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Asegurarse de que el sistema FAISS esté inicializado

```bash
# Si es la primera vez, ejecutar la migración
python3 migrate_to_faiss.py

# O verificar que existe el archivo
ls storage/graphs/faiss_system.pkl
```

### 3. Iniciar el servidor API

```bash
# Modo producción
python3 api_server.py

# Modo desarrollo (con auto-reload)
python3 api_server.py --reload

# Personalizar host y puerto
python3 api_server.py --host 0.0.0.0 --port 8080
```

### 4. Acceder a la documentación interactiva

Una vez iniciado el servidor, visita:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 Endpoints Disponibles

### POST /api/v1/query
Realizar consulta al sistema RAG.

**Request:**
```json
{
  "query": "¿Cuáles son los procedimientos principales?",
  "k": 5,
  "k_roots": 5,
  "include_context": true
}
```

**Response:**
```json
{
  "query": "¿Cuáles son los procedimientos principales?",
  "answer": "Los procedimientos principales son...",
  "chunks": [
    {
      "chunk_id": "chunk_123",
      "content": "Contenido del fragmento...",
      "score": 0.95,
      "document": "manual_tecnico.pdf"
    }
  ],
  "documents_used": ["manual_tecnico.pdf"],
  "processing_time": 1.23,
  "timestamp": "2025-10-13T10:30:00"
}
```

### GET /api/v1/health
Verificar estado del sistema.

**Response:**
```json
{
  "status": "healthy",
  "faiss_loaded": true,
  "llm_connected": true,
  "details": {
    "documents": 10,
    "indexed_roots": 10
  }
}
```

### GET /api/v1/stats
Obtener estadísticas del sistema.

**Response:**
```json
{
  "total_documents": 10,
  "total_chunks": 250,
  "indexed_roots": 10,
  "system_status": "operational",
  "faiss_index_size": 10
}
```

### GET /api/v1/documents
Listar documentos disponibles.

**Response:**
```json
[
  {
    "document_id": "manual_tecnico.pdf",
    "root_chunk_id": "chunk_root_001",
    "total_chunks": 25
  }
]
```

## 🧪 Ejemplos de Uso

### cURL

```bash
# Consulta básica
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Qué es este documento?"}'

# Health check
curl "http://localhost:8000/api/v1/health"

# Estadísticas
curl "http://localhost:8000/api/v1/stats"

# Listar documentos
curl "http://localhost:8000/api/v1/documents"
```

### Python requests

```python
import requests

# Realizar consulta
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query": "¿Cuáles son los procedimientos principales?",
        "k": 5,
        "k_roots": 5,
        "include_context": True
    }
)

data = response.json()
print(f"Respuesta: {data['answer']}")
print(f"Documentos usados: {data['documents_used']}")
print(f"Tiempo de procesamiento: {data['processing_time']}s")
```

### JavaScript fetch

```javascript
// Realizar consulta
const response = await fetch('http://localhost:8000/api/v1/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: '¿Cuáles son los procedimientos principales?',
    k: 5,
    k_roots: 5,
    include_context: true
  })
});

const data = await response.json();
console.log('Respuesta:', data.answer);
console.log('Documentos:', data.documents_used);
```

## 🏗️ Arquitectura

```
api_server.py              # Servidor principal FastAPI
src/api/
  ├── __init__.py         # Inicialización del módulo
  ├── models.py           # Modelos Pydantic (request/response)
  ├── routes.py           # Definición de endpoints
  └── service.py          # Lógica de negocio (wrapper del sistema RAG)
```

### Flujo de una Consulta

1. **Cliente** → Envía POST a `/api/v1/query`
2. **routes.py** → Recibe request, valida con Pydantic
3. **service.py** → Procesa consulta:
   - Busca en FAISS (reutiliza lógica existente)
   - Prepara contexto (reutiliza lógica existente)
   - Genera respuesta con LLM (reutiliza lógica existente)
4. **routes.py** → Formatea respuesta
5. **Cliente** ← Recibe respuesta JSON

## 🔒 Seguridad

### Recomendaciones para Producción

1. **Habilitar autenticación**:
   ```python
   # Agregar en routes.py
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   @query_router.post("/query", dependencies=[Depends(security)])
   ```

2. **Configurar CORS específicos**:
   ```python
   # En api_server.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://tu-dominio.com"],  # Especificar dominios
       ...
   )
   ```

3. **Rate limiting**:
   ```bash
   pip install slowapi
   ```

4. **HTTPS con certificados SSL**:
   ```bash
   uvicorn api_server:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
   ```

## ⚙️ Configuración

El servidor usa las mismas variables de entorno del sistema RAG (archivo `.env`):

```bash
# Ollama
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11435

# Sistema RAG (no requiere cambios)
CHUNK_SIZE=2000
EMBEDDING_DIM=768
...
```

## 🐳 Docker (Opcional)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python3", "api_server.py", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Construir y ejecutar
docker build -t lumina-rag-api .
docker run -p 8000:8000 --env-file .env lumina-rag-api
```

## 📊 Monitoreo

### Logs

Los logs se escriben en consola con formato estructurado:

```
2025-10-13 10:30:00 - src.api.service - INFO - Procesando consulta: ¿Cuáles son...
2025-10-13 10:30:01 - src.api.service - INFO - ✅ Respuesta generada exitosamente
2025-10-13 10:30:01 - src.api.routes - INFO - Consulta procesada exitosamente en 1.23s
```

### Métricas

Para métricas avanzadas, integrar con Prometheus:

```bash
pip install prometheus-fastapi-instrumentator
```

## 🛠️ Desarrollo

### Ejecutar en modo desarrollo

```bash
python3 api_server.py --reload
```

### Ejecutar tests (cuando estén disponibles)

```bash
pytest tests/api/
```

## 🚨 Troubleshooting

### Error: "Sistema no inicializado"

**Causa**: No existe `storage/graphs/faiss_system.pkl`

**Solución**:
```bash
python3 migrate_to_faiss.py
```

### Error: "No se pudo conectar con Ollama"

**Causa**: Ollama no está corriendo

**Solución**:
```bash
# Verificar que Ollama esté activo
curl http://localhost:11435/api/tags

# O iniciar Ollama
cd ../LuminaMO_Model_IA
docker-compose up -d
```

### Error: "FAISS system not found"

**Causa**: No se ha ejecutado la indexación

**Solución**:
```bash
# 1. Indexar documentos
python3 index.py

# 2. Migrar a FAISS
python3 migrate_to_faiss.py
```

## 📝 Notas Importantes

- ✅ **NO se modifica** la lógica del modelo, grafo ni arquitectura existente
- ✅ La API es un **wrapper** sobre `query_faiss.py` y `FAISSQuerySystem`
- ✅ Todo el procesamiento usa los **mismos métodos** que el sistema de consola
- ✅ Compatible con el sistema de consola (puedes usar ambos simultáneamente)

## 🔗 Enlaces

- [Documentación principal](../README.md)
- [Sistema de consultas original](../query_faiss.py)
- [Arquitectura FAISS](../FAISS_IMPLEMENTATION_SUMMARY.md)

---

**Desarrollado para mantener 100% compatibilidad con el sistema RAG existente**
