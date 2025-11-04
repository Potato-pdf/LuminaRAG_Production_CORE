"""
Servicio de consultas refactorizado.
Orquesta los diferentes módulos para procesar consultas RAG.
"""
import logging
from typing import List

from .collection_loader import CollectionLoader
from .query_processor import QueryProcessor
from .legacy_query_handler import LegacyQueryHandler
from api.querry_api.models import QueryResponse, SystemStats, DocumentInfo, HealthResponse

logger = logging.getLogger(__name__)


class QueryService:
    """
    Servicio principal de consultas RAG.
    Orquesta carga de colecciones y procesamiento de consultas.
    """
    
    def __init__(self):
        self.collection_loader = CollectionLoader()
        self.query_processor = QueryProcessor()
        self.legacy_handler = LegacyQueryHandler()
        self._initialized = False
    
    def initialize(self):
        """Inicializar todos los componentes del servicio"""
        if self._initialized:
            logger.warning("Sistema ya inicializado")
            return
        
        logger.info("Inicializando sistema RAG...")
        
        # Inicializar procesador de consultas
        self.query_processor.initialize()
        
        # Inicializar handler legacy (opcional)
        try:
            self.legacy_handler.initialize()
        except Exception as e:
            logger.warning(f"Legacy handler no disponible: {e}")
        
        self._initialized = True
        logger.info("🎉 Sistema RAG inicializado correctamente")
    
    def process_query_by_company(
        self, 
        query: str, 
        empresa: str, 
        private: bool, 
        k: int = 5
    ) -> QueryResponse:
        """
        Procesar consulta específica para una empresa y tipo de documento
        
        Args:
            query: Texto de la consulta
            empresa: Nombre de la empresa
            private: Si consultar documentos privados o públicos
            k: Número de chunks a recuperar
            
        Returns:
            QueryResponse con la respuesta generada
        """
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")
        
        # Cargar colección específica
        collection_system = self.collection_loader.load_collection(empresa, private)
        if not collection_system:
            raise RuntimeError(
                f"No se pudo cargar colección para {empresa} "
                f"({'privado' if private else 'público'})"
            )
        
        # Procesar consulta
        return self.query_processor.process_query(query, collection_system, k)
    
    def process_query(
        self, 
        query: str, 
        k: int = 5, 
        k_roots: int = 5,
        include_context: bool = True
    ) -> QueryResponse:
        """
        Procesar consulta usando sistema legacy (compatibilidad)
        
        Args:
            query: Texto de la consulta
            k: Número de chunks a recuperar
            k_roots: Número de raíces a considerar
            include_context: Si incluir contexto adicional
            
        Returns:
            QueryResponse con la respuesta generada
        """
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")
        
        return self.legacy_handler.process_query(query, k, k_roots, include_context)
    
    def get_stats(self) -> SystemStats:
        """Obtener estadísticas del sistema"""
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")
        
        return self.legacy_handler.get_stats()
    
    def get_documents(self) -> List[DocumentInfo]:
        """Obtener lista de documentos disponibles"""
        if not self._initialized:
            raise RuntimeError("Sistema no inicializado")
        
        return self.legacy_handler.get_documents()
    
    def health_check(self) -> HealthResponse:
        """Verificar estado del sistema"""
        if not self._initialized:
            return HealthResponse(
                status="unhealthy",
                faiss_loaded=False,
                llm_connected=False,
                details={"error": "Sistema no inicializado"}
            )
        
        # Verificar query processor
        query_health = self.query_processor._initialized and self.query_processor.llm is not None
        
        # Verificar legacy handler
        legacy_health = self.legacy_handler.health_check()
        
        # Combinar resultados
        status = "healthy" if query_health else "degraded"
        
        return HealthResponse(
            status=status,
            faiss_loaded=True,
            llm_connected=query_health,
            details={
                "query_processor": "operational" if query_health else "failed",
                "legacy_handler": legacy_health.status,
                "collections_cached": len(self.collection_loader.collection_cache)
            }
        )
