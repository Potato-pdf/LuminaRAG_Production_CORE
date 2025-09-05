"""
Flujo RAG Integrado con Grafo de Documentos
==========================================

Este módulo implementa el flujo completo de RAG con integración del grafo:

1. PDFs → LlamaParse → Documentos estructurados
2. Documentos → Chunking → Chunks individuales  
3. Chunks → Vector Database (Milvus) + Document Graph
4. Consultas → Vector Search + Graph Navigation → Respuestas contextualizadas

El grafo preserva la estructura del documento y permite navegación contextual.
"""

import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Imports del sistema RAG
from src.db_milvus.connection import connect_milvus
from src.db_milvus.schemas.schema_comercial import create_schema_comercial
from src.embedding.multilingual import choice_embedding
from src.parse_docs import parse_documents
from src.create_vectors.create_vector_milvus import create_vectors
from src.model_ai import connect_ollama
from src.create_index.create_index_llamaindex import create_index_llamaindex
from src.config import CHUNKING_CONFIG, PATH_CONFIG

# Imports del sistema de grafo
from src.document_graph import SimpleDocumentGraph, create_simple_rag_graph


class IntegratedRAGWithGraph:
    """
    Sistema RAG integrado que combina vectores + grafo para mantener contexto.
    
    Pipeline completo:
    1. Cargar y parsear PDFs con LlamaParse
    2. Crear chunks con preservación de estructura
    3. Almacenar en vector database (Milvus)
    4. Crear grafo de documentos para navegación contextual
    5. Proporcionar consultas híbridas (vector + grafo)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializar el sistema RAG integrado"""
        self.api_key = api_key or os.environ.get("LLAMA_CLOUD_API_KEY") or os.environ.get("LLAMA_API_KEY")
        
        # Componentes principales
        self.conn = None
        self.collection_name = None
        self.embedding_model = None
        self.vector_store = None
        self.llm = None
        self.index = None
        self.document_graph = None
        
        # Datos procesados
        self.raw_documents = []
        self.chunks_data = []
        
        print("🚀 Sistema RAG integrado con grafo inicializado")
    
    def setup_infrastructure(self):
        """Configurar la infraestructura base (DB, embeddings, LLM)"""
        print("\n📋 Configurando infraestructura...")
        
        # 1. Conexión a Milvus
        self.conn = connect_milvus()
        print("✅ Conectado a Milvus")
        
        # 2. Crear schema
        self.collection_name = create_schema_comercial()
        print(f"✅ Schema creado: {self.collection_name}")
        
        # 3. Modelo de embedding
        self.embedding_model = choice_embedding()
        print(f"✅ Modelo de embedding: {self.embedding_model}")
        
        # 4. Vector store
        self.vector_store = create_vectors(self.collection_name, self.embedding_model)
        print("✅ Vector store configurado")
        
        # 5. LLM
        self.llm = connect_ollama()
        print("✅ LLM conectado")
    
    def load_and_parse_documents(self, directory_path: str = None):
        """Cargar y parsear documentos PDF con LlamaParse"""
        print("\n📄 Cargando y parseando documentos...")
        
        directory_path = directory_path or PATH_CONFIG["pdf_directory"]
        
        try:
            self.raw_documents = parse_documents(
                directory_path=directory_path,
                api_key=self.api_key
            )
            print(f"✅ {len(self.raw_documents)} documentos parseados con LlamaParse")
            
        except Exception as e:
            print(f"❌ Error con LlamaParse: {e}")
            print("🔄 Usando método tradicional de lectura PDF...")
            
            # Fallback a método tradicional
            from src.read_docs.read_pdf import read_pdf
            self.raw_documents = read_pdf()
            print(f"✅ {len(self.raw_documents)} documentos leídos (método tradicional)")
        
        return self.raw_documents
    
    def create_vector_index(self):
        """Crear índice vectorial con chunking personalizado"""
        print("\n🔍 Creando índice vectorial...")
        
        if not self.raw_documents:
            raise ValueError("No hay documentos cargados. Ejecuta load_and_parse_documents() primero.")
        
        # Crear índice con configuración de chunking
        self.index = create_index_llamaindex(
            documents=self.raw_documents,
            vector_store=self.vector_store,
            embed_model=self.embedding_model,
            **CHUNKING_CONFIG
        )
        
        print(f"✅ Índice vectorial creado con {len(self.index.docstore.docs)} nodos")
        return self.index
    
    def extract_chunks_for_graph(self):
        """Extraer chunks del índice para crear el grafo de documentos"""
        print("\n🕸️  Extrayendo chunks para el grafo...")
        
        if not self.index:
            raise ValueError("El índice vectorial no está creado. Ejecuta create_vector_index() primero.")
        
        # Extraer chunks del índice
        self.chunks_data = []
        nodes = list(self.index.docstore.docs.values())
        
        for i, node in enumerate(nodes):
            chunk_data = {
                'chunk_id': node.node_id,
                'content': node.get_content(),
                'metadata': {
                    'file_name': node.metadata.get('file_name', 'unknown'),
                    'file_path': node.metadata.get('file_path', ''),
                    'page_label': node.metadata.get('page_label', ''),
                    'window': node.metadata.get('window', ''),
                    'original_text': node.metadata.get('original_text', ''),
                    'chunk_index': i
                }
            }
            self.chunks_data.append(chunk_data)
        
        print(f"✅ {len(self.chunks_data)} chunks extraídos para el grafo")
        return self.chunks_data
    
    def create_document_graph(self):
        """Crear grafo de documentos para preservar estructura y contexto"""
        print("\n📊 Creando grafo de documentos...")
        
        if not self.chunks_data:
            raise ValueError("No hay chunks disponibles. Ejecuta extract_chunks_for_graph() primero.")
        
        # Crear grafo usando los chunks
        self.document_graph = create_simple_rag_graph(self.chunks_data)
        
        # Mostrar estadísticas
        stats = self.document_graph.get_stats()
        print(f"✅ Grafo creado - Nodos: {stats['nodes']}, Conexiones: {stats['edges']}")
        
        return self.document_graph
    
    def setup_complete_system(self, directory_path: str = None):
        """Configurar todo el sistema completo de una vez"""
        print("🔄 Configurando sistema RAG completo con grafo...")
        print("=" * 60)
        
        # 1. Infraestructura
        self.setup_infrastructure()
        
        # 2. Documentos
        self.load_and_parse_documents(directory_path)
        
        # 3. Índice vectorial
        self.create_vector_index()
        
        # 4. Extraer chunks
        self.extract_chunks_for_graph()
        
        # 5. Crear grafo
        self.create_document_graph()
        
        print("\n🎉 ¡Sistema RAG con grafo configurado completamente!")
        print("=" * 60)
        return True
    
    def hybrid_query(self, query: str, use_graph_context: bool = True, top_k_graph: int = 3):
        """
        Realizar consulta híbrida usando vectores + grafo para mantener contexto
        
        Args:
            query: Consulta del usuario
            use_graph_context: Si usar contexto del grafo
            top_k_graph: Número de chunks relacionados a incluir del grafo
        """
        print(f"\n🔍 Procesando consulta: '{query}'")
        print("-" * 50)
        
        if not self.index or not self.llm:
            raise ValueError("Sistema no está configurado. Ejecuta setup_complete_system() primero.")
        
        # 1. Consulta vectorial tradicional
        query_engine = self.index.as_query_engine(llm=self.llm)
        vector_response = query_engine.query(query)
        
        print("📄 Respuesta vectorial obtenida")
        
        # 2. Si se solicita, enriquecer con contexto del grafo
        if use_graph_context and self.document_graph:
            print("🕸️  Enriqueciendo con contexto del grafo...")
            
            # Obtener chunks más importantes del grafo
            important_chunks = self.document_graph.get_most_important_chunks(top_k=top_k_graph)
            
            # Construir contexto adicional
            graph_context = "\n\nContexto adicional del grafo de documentos:\n"
            for chunk_id, importance in important_chunks:
                content = self.document_graph.get_chunk_content(chunk_id)
                if content:
                    graph_context += f"[Importancia: {importance:.3f}] {content[:200]}...\n"
            
            # Consulta enriquecida
            enriched_query = f"{query}\n\n{graph_context}"
            enriched_response = query_engine.query(enriched_query)
            
            print("✅ Respuesta enriquecida con contexto del grafo")
            return {
                'vector_response': str(vector_response),
                'enriched_response': str(enriched_response),
                'graph_context_used': True,
                'important_chunks': important_chunks
            }
        
        return {
            'vector_response': str(vector_response),
            'enriched_response': str(vector_response),
            'graph_context_used': False,
            'important_chunks': []
        }
    
    def get_system_stats(self):
        """Obtener estadísticas completas del sistema"""
        stats = {
            'documents_loaded': len(self.raw_documents),
            'vector_index_nodes': len(self.index.docstore.docs) if self.index else 0,
            'graph_stats': self.document_graph.get_stats() if self.document_graph else {},
            'chunks_processed': len(self.chunks_data),
            'infrastructure_ready': all([
                self.conn, self.collection_name, self.embedding_model, 
                self.vector_store, self.llm
            ])
        }
        return stats
    
    def analyze_document_structure(self, chunk_id: str):
        """Analizar la estructura de un documento específico usando el grafo"""
        if not self.document_graph:
            return {"error": "Grafo no está disponible"}
        
        # Análisis de conectividad
        connectivity = self.document_graph.analyze_connectivity(chunk_id)
        
        # Vecinos cercanos
        neighbors = self.document_graph.get_chunk_neighbors(chunk_id, radius=2)
        
        # Contenido del chunk
        content = self.document_graph.get_chunk_content(chunk_id)
        
        return {
            'chunk_id': chunk_id,
            'content_preview': content[:200] if content else "No disponible",
            'connectivity': connectivity,
            'neighbors': neighbors,
            'graph_analysis': True
        }


# ============================================================================
# FUNCIÓN DE CONVENIENCIA PARA USAR EL SISTEMA
# ============================================================================

def create_integrated_rag_system(directory_path: str = None, api_key: str = None):
    """
    Crear y configurar sistema RAG completo con grafo de una vez.
    
    Args:
        directory_path: Directorio con PDFs (opcional, usa configuración por defecto)
        api_key: API key de LlamaParse (opcional, usa variable de entorno)
    
    Returns:
        IntegratedRAGWithGraph: Sistema configurado y listo para usar
    """
    system = IntegratedRAGWithGraph(api_key=api_key)
    system.setup_complete_system(directory_path)
    return system
