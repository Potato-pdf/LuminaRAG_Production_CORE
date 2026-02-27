from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging

from .models import DocumentToIndex, IndexResponse
from .service_refactored import IndexService
from api.querry_api.models import QueryResponse, ErrorResponse, QueryRequest

logger = logging.getLogger(__name__)

# Router para indexación
index_router = APIRouter()

# Router para consultas (si se necesita)
query_router = APIRouter()

# Variable global para el servicio (inyectada por dependency)
def get_index_service():
    """Placeholder para dependency injection"""
    # Esta función será sobreescrita por el dependency del servidor
    pass


@index_router.post(
    "/index",
    response_model=IndexResponse,
    responses={
        400: {"model": dict},
        500: {"model": dict}
    },
    summary="Indexar documentos desde S3",
    description="Indexa documentos desde S3 organizados por empresa/privacidad y los guarda en colecciones FAISS específicas"
)
async def index_documents_endpoint(request: DocumentToIndex):
    """
    Indexar documentos para una empresa específica.

    Descarga documentos desde S3 según la estructura empresa/privacidad/,
    los procesa y los indexa en la colección correspondiente.
    """
    try:
        logger.info(f"Indexación solicitada para empresa {request.empresa}, privado: {request.private}")

        # Importar servicio desde el módulo principal
        from api_server import index_service

        if index_service is None:
            raise HTTPException(
                status_code=503,
                detail="Servicio de indexación no disponible."
            )

        # Procesar indexación
        response = index_service.index_documents(
            empresa=request.empresa,
            private=request.private,
            force_reindex=request.force_reindex
        )

        logger.info(f"Indexación completada: {response.documents_processed} documentos, {response.chunks_created} chunks")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en indexación: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error en indexación: {str(e)}"
        )


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
