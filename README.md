# Lumina RAG API - Sistema Comercial Multi-Tenant

Sistema RAG (Retrieval-Augmented Generation) multi-tenant con autenticación, gestión de documentos y panel de administración.

## 🚀 Características

- ✅ **Autenticación JWT** - Login seguro con tokens de acceso y refresco
- ✅ **API Keys** - Acceso programático para integraciones
- ✅ **Multi-Tenant** - Aislamiento completo de datos por empresa
- ✅ **CRUD de Documentos** - Upload, gestión y eliminación de documentos
- ✅ **Indexación FAISS** - Búsqueda semántica rápida
- ✅ **AWS S3** - Almacenamiento escalable de documentos
- ✅ **Panel Admin** - Gestión de empresas y usuarios
- ✅ **Rate Limiting** - Protección contra abuso
- ✅ **PostgreSQL** - Base de datos relacional robusta

---

## 📋 Requisitos Previos

- Docker y Docker Compose
- AWS Account (para S3)
- LlamaCloud API Key (para parsing de documentos)
- Ollama (para LLM) - opcional, puede estar en otro contenedor

---

## 🛠️ Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd LuminaRAG_Comercial
```

### 2. Configurar Variables de Entorno

Copiar el archivo de ejemplo y configurar:

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```bash
# Credenciales AWS (REQUERIDO)
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
S3_BUCKET=tu-bucket-name

# LlamaCloud API (REQUERIDO)
LLAMA_CLOUD_API_KEY=llx-tu-api-key

# Security (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=genera-una-clave-secreta-segura-aqui
```

### 3. Crear Red Docker

```bash
docker network create lumina_network
```

### 4. Levantar Servicios

```bash
docker-compose up -d --build
```

### 5. Verificar Estado

```bash
# Ver logs
docker logs -f lumina_rag_api

# Health check
curl http://localhost:3205/health

# Documentación interactiva
open http://localhost:3205/docs
```

---

## 📚 API Endpoints

### 🔐 Autenticación (`/api/v1/auth`)

#### Registro de Usuario
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "usuario@empresa.com",
  "password": "SecurePass123!",
  "full_name": "Nombre Completo",
  "company_name": "Mi Empresa"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "usuario@empresa.com",
  "password": "SecurePass123!"
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Obtener Perfil Actual
```http
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

#### Crear API Key
```http
POST /api/v1/auth/api-keys
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Production API Key",
  "expires_in_days": 365
}
```

**Respuesta:**
```json
{
  "id": 1,
  "name": "Production API Key",
  "api_key": "lum_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "expires_at": "2026-12-31T00:00:00Z"
}
```

> ⚠️ **IMPORTANTE:** El API key solo se muestra una vez. Guárdalo en un lugar seguro.

#### Listar API Keys
```http
GET /api/v1/auth/api-keys
Authorization: Bearer {access_token}
```

#### Revocar API Key
```http
DELETE /api/v1/auth/api-keys/{key_id}
Authorization: Bearer {access_token}
```

---

### 📁 Gestión de Documentos (`/api/v1/documents`)

#### Upload de Documento
```http
POST /api/v1/documents
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: [archivo.pdf]
is_private: false
```

**Tipos de archivo permitidos:** `.pdf`, `.txt`, `.docx`, `.doc`, `.md`  
**Tamaño máximo:** 50MB

**Respuesta:**
```json
{
  "id": 1,
  "filename": "documento.pdf",
  "original_filename": "Mi Documento.pdf",
  "s3_key": "mi-empresa/public/documento.pdf",
  "file_type": "pdf",
  "file_size": 1048576,
  "file_size_mb": 1.0,
  "is_private": false,
  "company_id": 1,
  "uploaded_by": 1,
  "index_status": "pending",
  "created_at": "2025-12-31T13:00:00Z"
}
```

#### Listar Documentos
```http
GET /api/v1/documents?is_private=false&skip=0&limit=100
Authorization: Bearer {access_token}
```

**Parámetros de query:**
- `is_private` (opcional): `true` | `false` - Filtrar por privacidad
- `skip` (opcional): Número de documentos a saltar (paginación)
- `limit` (opcional): Máximo de documentos a retornar (default: 100)

#### Obtener Documento Específico
```http
GET /api/v1/documents/{document_id}
Authorization: Bearer {access_token}
```

#### Eliminar Documento
```http
DELETE /api/v1/documents/{document_id}
Authorization: Bearer {access_token}
```

> 📝 **Nota:** Solo el usuario que subió el documento o un superusuario puede eliminarlo.

#### Cambiar Privacidad de Documento
```http
PATCH /api/v1/documents/{document_id}/privacy
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "is_private": true
}
```

---

### 🔍 Consultas RAG (`/api/v1/query`)

#### Consulta Pública
```http
POST /api/v1/query/public/{empresa}
X-API-Key: lum_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Content-Type: application/json

{
  "query": "¿Cuál es el precio del producto?",
  "k": 5
}
```

#### Consulta Privada
```http
POST /api/v1/query/private/{empresa}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "query": "Información confidencial sobre...",
  "k": 5
}
```

**Parámetros:**
- `query`: Pregunta a realizar
- `k`: Número de chunks a recuperar (default: 5)

---

### 📊 Indexación (`/api/v1/index`)

#### Indexar Documentos
```http
POST /api/v1/index
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "empresa": "mi-empresa",
  "private": false,
  "force_reindex": false
}
```

**Parámetros:**
- `empresa`: Slug de la empresa
- `private`: Si indexar documentos privados o públicos
- `force_reindex`: Forzar re-indexación completa

---

### 👥 Administración (`/api/v1/admin`) - Solo Superusuarios

#### Crear Empresa
```http
POST /api/v1/admin/companies
Authorization: Bearer {superuser_token}
Content-Type: application/json

{
  "name": "Nueva Empresa",
  "slug": "nueva-empresa",
  "max_documents": 1000,
  "max_storage_gb": 50.0,
  "max_queries_per_month": 10000
}
```

#### Listar Empresas
```http
GET /api/v1/admin/companies?skip=0&limit=100
Authorization: Bearer {superuser_token}
```

#### Obtener Empresa
```http
GET /api/v1/admin/companies/{company_id}
Authorization: Bearer {superuser_token}
```

#### Obtener Estadísticas de Empresa
```http
GET /api/v1/admin/companies/{company_id}/stats
Authorization: Bearer {superuser_token}
```

**Respuesta:**
```json
{
  "id": 1,
  "name": "Mi Empresa",
  "slug": "mi-empresa",
  "is_active": true,
  "max_documents": 1000,
  "max_storage_gb": 50.0,
  "stats": {
    "document_count": 15,
    "storage_used_gb": 2.5,
    "storage_limit_gb": 50.0,
    "document_limit": 1000,
    "storage_percentage": 5.0,
    "document_percentage": 1.5
  }
}
```

#### Actualizar Empresa
```http
PUT /api/v1/admin/companies/{company_id}
Authorization: Bearer {superuser_token}
Content-Type: application/json

{
  "max_documents": 2000,
  "max_storage_gb": 100.0
}
```

#### Eliminar Empresa
```http
DELETE /api/v1/admin/companies/{company_id}
Authorization: Bearer {superuser_token}
```

#### Crear Usuario en Empresa
```http
POST /api/v1/admin/companies/{company_id}/users
Authorization: Bearer {superuser_token}
Content-Type: application/json

{
  "email": "nuevo@empresa.com",
  "password": "SecurePass123!",
  "full_name": "Nuevo Usuario",
  "is_superuser": false
}
```

#### Listar Usuarios de Empresa
```http
GET /api/v1/admin/companies/{company_id}/users
Authorization: Bearer {superuser_token}
```

---

### 🏥 Sistema (`/api/v1`)

#### Health Check
```http
GET /api/v1/health
```

#### Estadísticas del Sistema
```http
GET /api/v1/stats
Authorization: Bearer {access_token}
```

#### Listar Colecciones
```http
GET /api/v1/collections
Authorization: Bearer {access_token}
```

---

## 🔑 Autenticación

El sistema soporta **dos métodos de autenticación**:

### 1. JWT Tokens (Para usuarios)

```bash
# Obtener token
curl -X POST http://localhost:3205/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Usar token
curl -X GET http://localhost:3205/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
```

### 2. API Keys (Para integraciones)

```bash
# Crear API key (requiere JWT primero)
curl -X POST http://localhost:3205/api/v1/auth/api-keys \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Production Key"}'

# Usar API key
curl -X POST http://localhost:3205/api/v1/query/public/empresa \
  -H "X-API-Key: lum_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{"query":"test","k":5}'
```

---

## 🗄️ Base de Datos

### Estructura de Tablas

- **companies** - Empresas/clientes
- **users** - Usuarios del sistema
- **api_keys** - API keys para acceso programático
- **documents** - Documentos subidos
- **company_configs** - Configuración por empresa

### Acceso a PostgreSQL

```bash
# Conectar a la base de datos
docker exec -it lumina_postgres psql -U lumina_user -d lumina_rag

# Ver tablas
\dt

# Ver usuarios
SELECT id, email, full_name, is_superuser FROM users;

# Ver empresas
SELECT id, name, slug, max_documents FROM companies;
```

---

## 📦 Estructura del Proyecto

```
LuminaRAG_Comercial/
├── src/
│   ├── database/           # Modelos y repositorios
│   │   ├── models/         # SQLAlchemy models
│   │   └── repositories/   # Repository pattern
│   ├── auth/               # Autenticación y autorización
│   │   ├── jwt.py          # JWT tokens
│   │   ├── security.py     # Password hashing
│   │   ├── dependencies.py # FastAPI dependencies
│   │   ├── permissions.py  # Permission checkers
│   │   └── rate_limiter.py # Rate limiting
│   ├── api/
│   │   ├── auth/           # Endpoints de autenticación
│   │   ├── documents/      # Endpoints de documentos
│   │   ├── admin/          # Endpoints de administración
│   │   └── schemas/        # Pydantic schemas (DTOs)
│   ├── config/             # Configuración
│   └── ...
├── api_server.py           # Servidor FastAPI principal
├── docker-compose.yml      # Configuración Docker
├── requirements.txt        # Dependencias Python
└── .env                    # Variables de entorno
```

---

## 🧪 Testing

### Flujo Completo de Testing

```bash
# 1. Registrar usuario
curl -X POST http://localhost:3205/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User",
    "company_name": "Test Company"
  }'

# 2. Guardar el access_token de la respuesta
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 3. Upload documento
curl -X POST http://localhost:3205/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf" \
  -F "is_private=false"

# 4. Listar documentos
curl -X GET http://localhost:3205/api/v1/documents \
  -H "Authorization: Bearer $TOKEN"

# 5. Indexar documentos
curl -X POST http://localhost:3205/api/v1/index \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": "test-company",
    "private": false,
    "force_reindex": false
  }'

# 6. Realizar consulta
curl -X POST http://localhost:3205/api/v1/query/public/test-company \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué información contiene el documento?",
    "k": 5
  }'
```

---

## 🔒 Seguridad

### Características Implementadas

- ✅ **Password Hashing** - Bcrypt con salt automático
- ✅ **JWT Tokens** - Access (30min) + Refresh (7 días)
- ✅ **API Keys** - Hasheadas con SHA-256
- ✅ **Rate Limiting** - 60 requests/minuto por defecto
- ✅ **Soft Deletes** - Auditoría completa
- ✅ **CORS** - Configurable por origen
- ✅ **Permisos Granulares** - Por empresa y documento

### Recomendaciones de Producción

1. **Cambiar SECRET_KEY** en `.env`
2. **Configurar CORS** específico en `api_server.py`
3. **Usar HTTPS** con certificado SSL
4. **Configurar rate limiting** según necesidades
5. **Backup regular** de PostgreSQL
6. **Monitoreo** con Prometheus/Grafana

---

## 🐛 Troubleshooting

### Error: "Could not connect to database"

```bash
# Verificar que PostgreSQL está corriendo
docker ps | grep postgres

# Ver logs de PostgreSQL
docker logs lumina_postgres

# Reiniciar servicios
docker-compose restart
```

### Error: "Invalid API key"

- Verificar que el API key comienza con `lum_`
- Verificar que no ha expirado
- Verificar que está activo (no revocado)

### Error: "File too large"

- Tamaño máximo: 50MB
- Modificar `MAX_FILE_SIZE` en `src/api/documents/routes.py`

### Error: "S3 upload failed"

- Verificar credenciales AWS en `.env`
- Verificar permisos del bucket S3
- Verificar que el bucket existe

---

## 📊 Límites por Defecto

| Recurso | Límite Default | Configurable |
|---------|----------------|--------------|
| Documentos por empresa | 100 | ✅ Admin panel |
| Almacenamiento | 5 GB | ✅ Admin panel |
| Consultas/mes | 1,000 | ✅ Admin panel |
| Tamaño de archivo | 50 MB | ⚙️ Código |
| Rate limit | 60 req/min | ⚙️ Código |
| Token expiration | 30 min | ⚙️ .env |

---

## 🚀 Próximos Pasos / Mejoras Futuras

### Críticas para Producción

#### 1. Configurar Alembic para Migraciones de Base de Datos
**Estado:** ⚠️ Pendiente  
**Prioridad:** Alta para producción

**¿Qué es?** Alembic es una herramienta de migraciones de base de datos que permite:
- Versionado de cambios en la estructura de la BD
- Historial completo de modificaciones
- Rollback seguro de cambios
- Sincronización entre entornos (dev, staging, prod)

**Situación Actual:**  
El sistema usa `SQLAlchemy.create_all()` que crea las tablas automáticamente al iniciar. Esto funciona perfecto para desarrollo y testing, pero en producción es mejor tener control granular de los cambios.

**Cómo implementar:**
```bash
# 1. Instalar Alembic
pip install alembic==1.13.1

# 2. Inicializar
alembic init alembic

# 3. Configurar alembic.ini con tu DATABASE_URL

# 4. Crear migración inicial
alembic revision --autogenerate -m "Initial schema"

# 5. Aplicar migración
alembic upgrade head
```

**Beneficios:**
- ✅ Control de versiones de BD
- ✅ Cambios rastreables y reversibles
- ✅ Deploys más seguros
- ✅ Colaboración en equipo mejorada

---

#### 2. Implementar Indexación Asíncrona
**Estado:** ⚠️ Pendiente  
**Prioridad:** Alta

Actualmente la indexación es síncrona. Para producción se recomienda:
- Usar Celery o similar para tareas en background
- Queue de indexación (Redis/RabbitMQ)
- Notificaciones de progreso vía webhooks

#### 3. Tests Unitarios e Integración
**Estado:** ⚠️ Pendiente  
**Prioridad:** Alta

Crear suite de tests con pytest:
- Tests unitarios de repositorios
- Tests de endpoints API
- Tests de autenticación
- Tests de permisos

---

### Mejoras Opcionales

- [ ] Implementar webhooks para eventos
- [ ] Agregar métricas y analytics (Prometheus/Grafana)
- [ ] Sistema de facturación (Stripe)
- [ ] Email verification en registro
- [ ] Password reset functionality
- [ ] Audit logs completos
- [ ] CDN para documentos (CloudFront)
- [ ] Client SDKs (Python, JavaScript)

---

## 📞 Soporte

Para preguntas o problemas:

1. Revisar la documentación en `/docs`
2. Verificar logs: `docker logs -f lumina_rag_api`
3. Consultar el walkthrough en `.gemini/antigravity/brain/*/walkthrough.md`

---

## 📄 Licencia

[Especificar licencia]

---

## 🙏 Créditos

Desarrollado con:
- FastAPI
- PostgreSQL
- AWS S3
- FAISS
- LlamaIndex
- Ollama
