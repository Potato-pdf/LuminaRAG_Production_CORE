# 🌟 LuminaMO_RAG - Sistema RAG Jerárquico Avanzado

Sistema de Recuperación Aumentada Generativa (RAG) con arquitectura jerárquica de grafos, embeddings multilingües y análisis de grafos avanzado. **Ahora con API especializada por empresa y control de privacidad**.

## ✨ Novedades v2.0

- 🏢 **Indexación por Empresa**: Documentos organizados en colecciones específicas por empresa
- 🔒 **Control de Acceso**: Separación automática entre documentos públicos y privados
- 🚀 **API REST Completa**: Endpoints dedicados para indexación y consultas filtradas
- 📊 **Colecciones Dinámicas**: Sistema FAISS que crea colecciones `empresa_public` y `empresa_private`
- 🐳 **Docker Optimizado**: Despliegue contenerizado completo

## 🏗️ Arquitectura

### 🌳 Grafos Jerárquicos + Control de Empresa
```
S3 Bucket Structure:
FINFERSSA/
├── public/
│   ├── manual_usuario.pdf
│   └── guia_instalacion.docx
└── private/
    ├── contrato_servicio.pdf
    └── datos_financieros.xlsx

FAISS Collections:
├── FINFERSSA_public.faiss    # Documentos públicos
└── FINFERSSA_private.faiss   # Documentos privados
```

### 🔧 Componentes Principales
- **api_server.py**: Servidor FastAPI con endpoints especializados
- **index.py**: Indexador principal con esquema jerárquico
- **query_by_company.py**: Consultas interactivas por empresa
- **src/api/index/**: Endpoints de indexación por empresa
- **src/api/querry_api/**: Endpoints de consulta con filtros

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# Desplegar completo
./deploy.sh

# Ver logs
docker-compose logs -f
```

### Opción 2: Desarrollo Local

```bash
# Configurar entorno
./dev.sh

# Ejecutar servidor
python api_server.py --reload
```

## 📋 API Endpoints

### Indexación
```http
POST /api/v1/index
Content-Type: application/json

{
  "empresa": "FINFERSSA",
  "titulo": "Documento de prueba",
  "private": false
}
```
**Respuesta**: Indexa documentos desde S3 y crea colección `FINFERSSA_public.faiss`

### Consultas por Empresa

#### Documentos Públicos
```http
POST /api/v1/query/public/{empresa}
Content-Type: application/json

{
  "query": "¿Qué información hay sobre contratos?",
  "k": 5
}
```
**Ejemplo**: `POST /api/v1/query/public/FINFERSSA`

#### Documentos Privados
```http
POST /api/v1/query/private/{empresa}
Content-Type: application/json

{
  "query": "¿Qué información confidencial hay?",
  "k": 5
}
```
**Ejemplo**: `POST /api/v1/query/private/FINFERSSA`

### Sistema
- `GET /api/v1/health` - Estado del sistema
- `GET /api/v1/stats` - Estadísticas del sistema
- `GET /api/v1/documents` - Lista de documentos

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Ollama (para LLM)
OLLAMA_BASE_URL=http://localhost:11434

# LlamaCloud (para parsing de documentos)
LLAMA_CLOUD_API_KEY=tu_api_key_aqui

# AWS S3
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
S3_BUCKET_NAME=tu_bucket
S3_REGION=us-east-1
```

### Estructura S3 Requerida

```
tu-bucket/
├── FINFERSSA/
│   ├── public/
│   │   ├── manual.pdf
│   │   └── guia.docx
│   └── private/
│       ├── contrato.pdf
│       └── datos.xlsx
└── OTRA_EMPRESA/
    ├── public/
    └── private/
```

## 🧪 Pruebas

```bash
# Pruebas completas de API
python test_api_complete.py

# Documentación interactiva
# http://localhost:8000/docs
```

## � Flujo de Trabajo

1. **Indexación**: `POST /api/v1/index` con `{"empresa": "FINFERSSA", "private": false}`
2. **Sistema**: Crea colección `FINFERSSA_public.faiss` con documentos de `FINFERSSA/public/`
3. **Consulta Pública**: `POST /api/v1/query/public/FINFERSSA` busca solo en documentos públicos
4. **Consulta Privada**: `POST /api/v1/query/private/FINFERSSA` busca solo en documentos privados

## � Monitoreo

```bash
# Health check
curl http://localhost:8000/health

# Ver logs
docker-compose logs -f lumina-rag-api
```

## 🛠️ Desarrollo

### Estructura Actualizada
```
LuminaMO_RAG/
├── api_server.py              # 🚀 Servidor FastAPI principal
├── test_api_complete.py        # 🧪 Pruebas de API
├── src/
│   ├── api/
│   │   ├── index/             # 📥 Endpoints de indexación
│   │   └── querry_api/        # 🔍 Endpoints de consulta
│   ├── parse_docs/            # 📄 Parsing con metadata S3
│   ├── FAISS/                 # 🚀 Sistema FAISS
│   └── config/                # ⚙️ Configuración
├── data/                      # 💾 Datos persistentes
├── docker-compose.yml         # 🐳 Configuración Docker
└── requirements.txt           # 📦 Dependencias
```

### Agregar Nueva Empresa

1. **Organizar en S3**: `empresa/public/` y `empresa/private/`
2. **Indexar**: 
   ```bash
   curl -X POST http://localhost:8000/api/v1/index \
     -H "Content-Type: application/json" \
     -d '{"empresa": "NUEVA_EMPRESA", "private": false}'
   ```
3. **Consultar**: 
   - Públicos: `/api/v1/query/public/NUEVA_EMPRESA`
   - Privados: `/api/v1/query/private/NUEVA_EMPRESA`

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

### 🔍 Búsqueda por Empresa
- **Colecciones Aisladas**: Cada empresa tiene sus propias colecciones FAISS
- **Control de Privacidad**: Separación automática público/privado
- **Filtrado Automático**: Las consultas solo acceden a documentos permitidos
- **Escalabilidad**: Nuevo sistema preparado para múltiples empresas

## ⚙️ Configuración Técnica

### CHUNKING_CONFIG
- `chunk_size`: Tamaño de fragmentos (default: 2000)
- `chunk_overlap`: Solapamiento entre fragmentos (default: 100)
- `chunk_window_size`: Ventana para SentenceWindowNodeParser (default: 3)

### EMBEDDING_CONFIG
- `embedding_dim`: Dimensión del vector (default: 768)
- `model_name`: Modelo de embedding (default: "efederici/e5-base-multilingual-4096")

### MILVUS_CONFIG
- `host`: Host de Milvus (default: "localhost")
- `port`: Puerto de Milvus (default: "19530")

### OLLAMA_CONFIG
- `model`: Modelo Ollama (default: "llama3.2")
- `base_url`: URL base Ollama (default: "http://localhost:11435")

## 🧪 Testing y Validación

```bash
# Pruebas de API completas
python test_api_complete.py

# Pruebas de arquitectura
python test/test_refactored_architecture.py

# Utilidades de gestión
python utils.py
```

## 🚨 Migración

Para migrar desde versiones anteriores:

```bash
# El sistema ahora usa colecciones dinámicas
# Los datos antiguos se mantienen compatibles
# Nueva funcionalidad disponible vía API
```

## 📈 Monitoreo y Estadísticas

```bash
# Estadísticas del sistema
curl http://localhost:8000/api/v1/stats

# Health check continuo
curl http://localhost:8000/health
```

---

� **Lumina RAG v2.0** - Sistema RAG empresarial con control de acceso y API especializada.

**Documentación completa**: http://localhost:8000/docs
