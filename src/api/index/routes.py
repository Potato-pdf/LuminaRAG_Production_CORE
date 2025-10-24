from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging

from api.querry_api.models import (
    QueryRequest, 
    QueryResponse, 
    SystemStats, 
    DocumentInfo, 
    HealthResponse,
    ErrorResponse
)
from api.querry_api.service import QueryService

logger = logging.getLogger(__name__)

# Router para consultas
query_router = APIRouter()

# Router para endpoints del sistema
system_router = APIRouter()


# Variable global para el servicio (inyectada por dependency)
def get_service():
    """Placeholder para dependency injection"""
    # Esta función será sobreescrita por el dependency del servidor
    pass


@query_router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse}
    },
    summary="Realizar consulta al sistema RAG",
    description="Procesa una consulta y retorna la respuesta generada por el LLM con contexto relevante"
)
async def query_endpoint(request: QueryRequest):
    """
    Endpoint principal de consultas.
    
    Recibe una consulta y parámetros opcionales, procesa la búsqueda
    en el sistema RAG y retorna la respuesta del LLM con chunks relevantes.
    """
    try:
        logger.info(f"Nueva consulta recibida: {request.query[:50]}...")
        
        # Importar servicio desde el módulo principal
        from api_server import query_service
        
        if query_service is None:
            raise HTTPException(
                status_code=503,
                detail="Servicio no disponible. Sistema no inicializado."
            )
        
        # Procesar consulta usando el servicio
        response = query_service.process_query(
            query=request.query,
            k=request.k,
            k_roots=request.k_roots,
            include_context=request.include_context
        )
        
        logger.info(f"Consulta procesada exitosamente en {response.processing_time:.2f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando consulta: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando consulta: {str(e)}"
        )


@system_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar estado del sistema",
    description="Retorna el estado de salud del sistema RAG (FAISS, LLM, etc.)"
)
async def health_endpoint():
    """
    Health check del sistema.
    
    Verifica que todos los componentes estén funcionando correctamente.
    """
    try:
        from api_server import query_service
        
        if query_service is None:
            return HealthResponse(
                status="unhealthy",
                faiss_loaded=False,
                llm_connected=False,
                details={"error": "Sistema no inicializado"}
            )
        
        health = query_service.health_check()
        return health
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return HealthResponse(
            status="unhealthy",
            faiss_loaded=False,
            llm_connected=False,
            details={"error": str(e)}
        )


@system_router.get(
    "/stats",
    response_model=SystemStats,
    summary="Obtener estadísticas del sistema",
    description="Retorna estadísticas sobre documentos indexados y estado del sistema"
)
async def stats_endpoint():
    """
    Estadísticas del sistema.
    
    Incluye información sobre documentos, chunks, raíces indexadas, etc.
    """
    try:
        from api_server import query_service
        
        if query_service is None:
            raise HTTPException(
                status_code=503,
                detail="Servicio no disponible"
            )
        
        stats = query_service.get_stats()
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


@system_router.get(
    "/documents",
    response_model=list[DocumentInfo],
    summary="Listar documentos disponibles",
    description="Retorna la lista de documentos indexados en el sistema"
)
async def documents_endpoint():
    """
    Listar documentos disponibles.
    
    Retorna información de todos los documentos indexados,
    incluyendo su ID, raíz y número de chunks.
    """
    try:
        from api_server import query_service
        
        if query_service is None:
            raise HTTPException(
                status_code=503,
                detail="Servicio no disponible"
            )
        
        documents = query_service.get_documents()
        return documents
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo documentos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo documentos: {str(e)}"
        )
