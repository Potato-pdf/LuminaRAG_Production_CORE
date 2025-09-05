"""
Configuración específica para el sistema de grafos de documentos.
Centraliza parámetros relacionados con la construcción y análisis del grafo.
"""
import os

# Configuración de construcción del grafo
GRAPH_CONFIG = {
    # Umbral de similitud para crear aristas semánticas
    "similarity_threshold": float(os.getenv("GRAPH_SIMILARITY_THRESHOLD", "0.7")),
    
    # Si preservar el orden de los documentos originales
    "preserve_document_order": os.getenv("GRAPH_PRESERVE_ORDER", "true").lower() == "true",
    
    # Radio de contexto para recuperación
    "default_context_radius": int(os.getenv("GRAPH_CONTEXT_RADIUS", "2")),
    
    # Máximo número de chunks en recuperación
    "max_retrieval_chunks": int(os.getenv("GRAPH_MAX_CHUNKS", "10")),
    
    # Estrategia de contexto por defecto
    "default_context_strategy": os.getenv("GRAPH_CONTEXT_STRATEGY", "adaptive"),
    
    # Configuración de análisis
    "enable_cycle_detection": os.getenv("GRAPH_DETECT_CYCLES", "true").lower() == "true",
    "enable_centrality_analysis": os.getenv("GRAPH_CENTRALITY", "true").lower() == "true",
    
    # Configuración de exportación
    "auto_export_graph": os.getenv("GRAPH_AUTO_EXPORT", "false").lower() == "true",
    "export_path": os.getenv("GRAPH_EXPORT_PATH", "graph_exports/"),
}

# Configuración de tipos de aristas
EDGE_TYPES = {
    "sequential": {
        "weight": 1.0,
        "description": "Orden natural del documento"
    },
    "semantic": {
        "weight": 0.8,
        "description": "Relación semántica entre chunks"
    },
    "reference": {
        "weight": 0.6,
        "description": "Referencia o cita dirigida"
    },
    "continuation": {
        "weight": 0.9,
        "description": "Continuación de tema o idea"
    }
}

# Configuración de estrategias de contexto
CONTEXT_STRATEGIES = {
    "sequential": {
        "description": "Solo contexto secuencial",
        "radius": 3,
        "include_semantic": False
    },
    "semantic": {
        "description": "Solo relaciones semánticas",
        "radius": 1,
        "include_semantic": True
    },
    "adaptive": {
        "description": "Combina secuencial y semántico",
        "radius": 2,
        "include_semantic": True
    },
    "full_document": {
        "description": "Documento completo",
        "radius": 999,
        "include_semantic": False
    }
}
