#!/usr/bin/env python3
"""
🌐 API REST PARA SISTEMA RAG LUMINA
====================================

API REST que expone el sistema de consultas RAG sin modificar
la lógica existente del modelo, grafo ni arquitectura.

Endpoints:
- POST /api/v1/query - Realizar consulta
- GET /api/v1/health - Estado del sistema
- GET /api/v1/stats - Estadísticas del sistema
- GET /api/v1/documents - Listar documentos disponibles
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import uvicorn
import logging

from api.querry_api.routes import query_router, system_router
from api.querry_api.service_refactored import QueryService
from api.index.routes import index_router
from api.index.service_refactored import IndexService

# Cargar configuración
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variable global para el servicio
query_service = None
index_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    global query_service, index_service
    
    # Startup
    logger.info("🚀 Iniciando API REST Lumina RAG...")
    try:
        query_service = QueryService()
        query_service.initialize()
        logger.info("✅ Sistema RAG de consultas inicializado correctamente")

        index_service = IndexService()
        index_service.initialize()
        logger.info("✅ Sistema de indexación inicializado correctamente")

        yield
    except Exception as e:
        logger.error(f"❌ Error inicializando sistemas: {e}")
        raise
    finally:
        # Shutdown
        logger.info("👋 Cerrando API REST Lumina RAG...")


# Crear aplicación FastAPI
app = FastAPI(
    title="Lumina RAG API",
    description="API REST para consultas al sistema RAG jerárquico con FAISS",
    version="1.0.0",
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


def get_query_service() -> QueryService:
    """Dependency para obtener el servicio de consultas"""
    if query_service is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado")
    return query_service


def get_index_service() -> IndexService:
    """Dependency para obtener el servicio de indexación"""
    if index_service is None:
        raise HTTPException(status_code=503, detail="Servicio de indexación no inicializado")
    return index_service


# Registrar routers
app.include_router(
    query_router,
    prefix="/api/v1",
    tags=["Consultas"],
    dependencies=[Depends(get_query_service)]
)

app.include_router(
    index_router,
    prefix="/api/v1",
    tags=["Indexación"],
    dependencies=[Depends(get_index_service)]
)

app.include_router(
    system_router,
    prefix="/api/v1",
    tags=["Sistema"],
    dependencies=[Depends(get_query_service)]
)


@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "name": "Lumina RAG API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            # Indexación
            "index": "POST /api/v1/index",
            # Consultas generales
            "query": "POST /api/v1/query",
            # Consultas por empresa
            "query_public": "POST /api/v1/query/public/{empresa}",
            "query_private": "POST /api/v1/query/private/{empresa}",
            # Sistema
            "health": "GET /api/v1/health",
            "stats": "GET /api/v1/stats",
            "documents": "GET /api/v1/documents"
        }
    }


@app.get("/health")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "service": "lumina-rag-api"
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Servidor API REST Lumina RAG")
    parser.add_argument("--host", default="0.0.0.0", help="Host del servidor")
    parser.add_argument("--port", type=int, default=8000, help="Puerto del servidor")
    parser.add_argument("--reload", action="store_true", help="Modo de desarrollo con auto-reload")
    
    args = parser.parse_args()
    
    logger.info(f"🌐 Iniciando servidor en http://{args.host}:{args.port}")
    logger.info(f"📚 Documentación disponible en http://{args.host}:{args.port}/docs")
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
