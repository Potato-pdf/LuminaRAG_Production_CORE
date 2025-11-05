# Lumina RAG API

Sistema RAG multi-tenant con FAISS e indexación incremental.

## 🐳 Docker

```bash
# Crear red
docker network create lumina_network

# Levantar
docker-compose up -d --build

# Logs
docker logs -f lumina_rag_api

# Detener
docker-compose down
```

## 📍 Endpoints

**Base URL:** `http://localhost:3205`

### Indexación

**POST** `/api/v1/index`
```json
{
  "empresa": "Test",
  "private": false,
  "force_reindex": false
}
```

### Queries

**POST** `/api/v1/query/public/{empresa}`
```json
{
  "query": "tu pregunta",
  "k": 5
}
```

**POST** `/api/v1/query/private/{empresa}`
```json
{
  "query": "tu pregunta",
  "k": 5
}
```

### Sistema

**GET** `/api/v1/health`

**GET** `/api/v1/system/stats`

**GET** `/api/v1/collections`

**GET** `/api/v1/documents/{empresa}/{privacy}`

## 🔧 Configuración

Variables en `.env`:
- `NETWORK_NAME=lumina_network`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BUCKET`
- `LLAMA_CLOUD_API_KEY`
- `OLLAMA_BASE_URL=http://ollama:11434`

## 📚 Docs

Swagger: `http://localhost:3205/docs`