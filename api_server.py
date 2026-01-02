#!/usr/bin/env python3
"""
🌐 API REST PARA SISTEMA RAG LUMINA - VERSIÓN COMERCIAL
========================================================

API REST multi-tenant con autenticación, gestión de documentos y panel admin.

Endpoints:
- /api/v1/auth - Autenticación (register, login, API keys)
- /api/v1/documents - Gestión de documentos (CRUD)
- /api/v1/admin - Panel de administración
- /api/v1/query - Consultas RAG
- /api/v1/index - Indexación de documentos
- /api/v1/health - Estado del sistema
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import uvicorn
import logging

# Cargar configuración
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    
    # Startup
    logger.info("🚀 Iniciando API REST Lumina RAG...")
    try:
        # Inicializar base de datos
        logger.info("📊 Inicializando base de datos...")
        from src.database import init_db
        init_db()
        logger.info("✅ Base de datos inicializada")
        
        yield
    except Exception as e:
        logger.error(f"❌ Error inicializando sistema: {e}")
        raise
    finally:
        # Shutdown
        logger.info("👋 Cerrando API REST Lumina RAG...")


# Crear aplicación FastAPI
app = FastAPI(
    title="Lumina RAG API - Commercial",
    description="API REST multi-tenant para consultas RAG con autenticación y gestión de documentos",
    version="2.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers de autenticación y gestión
logger.info("📦 Registrando routers de autenticación y gestión...")

from src.api.auth.routes import router as auth_router
from src.api.documents.routes import router as documents_router
from src.api.admin.routes import router as admin_router

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)

app.include_router(
    documents_router,
    prefix="/api/v1/documents",
    tags=["Documentos"]
)

app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["Administración"]
)

logger.info("✅ Routers de autenticación y gestión registrados")


# Endpoints básicos
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Lumina RAG API - Commercial Edition",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Multi-tenant authentication",
            "Document management (CRUD)",
            "Admin panel",
            "RAG queries",
            "API Keys support"
        ],
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Verificar conexión a base de datos
        from src.database import get_db
        
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": "2.0.0"
    }


@app.get("/api/v1/info")
async def api_info():
    """Información de la API"""
    return {
        "api_name": "Lumina RAG API",
        "version": "2.0.0",
        "edition": "Commercial Multi-Tenant",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "documents": "/api/v1/documents",
            "admin": "/api/v1/admin",
            "health": "/health",
            "docs": "/docs"
        },
        "features": {
            "authentication": ["JWT", "API Keys", "Refresh Tokens"],
            "document_management": ["Upload", "List", "Delete", "Privacy Control"],
            "admin_panel": ["Company CRUD", "User CRUD", "Statistics"],
            "security": ["Rate Limiting", "Role-based Access", "Soft Deletes"]
        }
    }


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT_LUMINA", 3205))
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
