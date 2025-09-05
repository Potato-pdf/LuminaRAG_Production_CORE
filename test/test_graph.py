"""
Test del sistema de grafos simplificado con NetworkX
===================================================

Este archivo prueba todas las funcionalidades del SimpleDocumentGraph
usando documentos REALES de la carpeta pdfs/.
"""

# Importar las funciones desde el módulo principal
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.document_graph import DocumentGraph, create_simple_rag_graph
from src.read_docs.read_pdf import read_pdf
from src.config import settings
from llama_index.core.node_parser import SentenceSplitter

# ============================================================================
# TEST CON DOCUMENTOS REALES
# ============================================================================

def test_with_real_documents():
    """
    Probar el grafo con documentos reales de la carpeta pdfs/
    """
    print("🧪 TEST: Usando documentos reales de la carpeta pdfs/\n")
    
    # Configurar rutas
    docs_directory = settings.PATH_CONFIG["pdf_directory"]
    print(f"📁 Directorio de documentos: {docs_directory}")
    
    # Leer los documentos
    print("\n📖 Leyendo documentos...")
    docs = read_pdf()
    
    if not docs:
        print("❌ No se encontraron documentos para procesar")
        return None
        
    print(f"✅ Se cargaron {len(docs)} documentos")
    
    # Crear chunks con LlamaIndex
    print("\n🔪 Creando chunks...")
    node_parser = SentenceSplitter(
        chunk_size=settings.CHUNKING_CONFIG["chunk_size"],
        chunk_overlap=settings.CHUNKING_CONFIG["chunk_overlap"]
    )
    
    chunks = node_parser.get_nodes_from_documents(docs)
    print(f"✅ Se crearon {len(chunks)} chunks")
    
    # Convertir chunks a formato para el grafo
    print("\n🔄 Preparando datos para el grafo...")
    chunks_data = []
    for i, chunk in enumerate(chunks):
        chunks_data.append({
            'id': f'chunk_{i}',
            'content': chunk.text,
            'metadata': {
                'file_name': chunk.metadata.get('file_name', 'unknown'),
                'page_label': chunk.metadata.get('page_label', 'unknown')
            }
        })
    
    # Crear el grafo con datos reales
    print(f"\n🕸️ Creando grafo con {len(chunks_data)} chunks reales...")
    mi_grafo = create_simple_rag_graph(chunks_data)
    
    return mi_grafo, chunks_data

def test_graph_functions(grafo, chunks_data):
    """
    Probar todas las funciones del grafo
    """
    print("\n🔍 Probando funciones del grafo:")
    
    # Obtener el primer chunk para tests
    primer_chunk = chunks_data[0]['id'] if chunks_data else 'chunk_0'
    
    # 1. Obtener contenido
    print(f"\n📄 Contenido de {primer_chunk}:")
    contenido = grafo.get_chunk_content(primer_chunk)
    if contenido:
        print(f"   {contenido[:100]}...")
    
    # 2. Encontrar chunks conectados
    print(f"\n🔗 Chunks conectados desde {primer_chunk}:")
    conectados = grafo.get_connected_chunks(primer_chunk)
    
    # 3. Encontrar chunks importantes (PageRank)
    print(f"\n⭐ Top 5 chunks más importantes:")
    importantes = grafo.get_most_important_chunks(5)
    
    # 4. Obtener vecinos
    if len(chunks_data) > 1:
        segundo_chunk = chunks_data[1]['id']
        print(f"\n👥 Vecinos de {segundo_chunk}:")
        vecinos = grafo.get_chunk_neighbors(segundo_chunk, radius=2)
    
    # 5. Encontrar caminos entre chunks
    if len(chunks_data) > 2:
        print(f"\n🛣️ Camino entre {primer_chunk} y chunk_2:")
        camino = grafo.find_path(primer_chunk, 'chunk_2')
    
    # 6. Estadísticas finales
    print(f"\n📊 Estadísticas finales del grafo:")
    stats = grafo.get_stats()
    
    # 7. Guardar el grafo
    print(f"\n💾 Guardando grafo...")
    grafo.save_graph("test_grafo_real")

if __name__ == "__main__":
    """
    EJECUTAR TESTS CON DOCUMENTOS REALES
    ====================================
    """
    try:
        # Test principal con documentos reales
        grafo, chunks_data = test_with_real_documents()
        
        if grafo and chunks_data:
            # Probar todas las funciones
            test_graph_functions(grafo, chunks_data)
            print("\n✅ ¡Test completado exitosamente!")
        else:
            print("\n❌ Error: No se pudieron cargar los documentos")
            
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
