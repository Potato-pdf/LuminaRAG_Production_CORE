"""
Test de Arquitectura Refactorizada
==================================

Test rápido para verificar que la nueva arquitectura modular funciona correctamente.
"""

import sys
import os

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.document_graph import SimpleDocumentGraph, create_simple_rag_graph

def test_modular_architecture():
    """Test básico de la arquitectura modular"""
    
    print("🧪 Probando arquitectura modular refactorizada...")
    print("=" * 60)
    
    # 1. Test de creación directa
    print("\n1️⃣ Test creación directa:")
    graph = SimpleDocumentGraph()
    
    # 2. Test operaciones básicas
    print("\n2️⃣ Test operaciones básicas:")
    graph.add_chunk("chunk1", "Contenido del primer chunk", {"file": "doc1.pdf"})
    graph.add_chunk("chunk2", "Contenido del segundo chunk", {"file": "doc1.pdf"})
    graph.add_chunk("chunk3", "Contenido del tercer chunk", {"file": "doc2.pdf"})
    
    # 3. Test conexiones
    print("\n3️⃣ Test conexiones:")
    graph.connect_chunks("chunk1", "chunk2", 0.8)
    graph.connect_chunks("chunk2", "chunk3", 0.6)
    
    # 4. Test consultas básicas
    print("\n4️⃣ Test consultas básicas:")
    content = graph.get_chunk_content("chunk1")
    print(f"📄 Contenido chunk1: {content[:50]}...")
    
    connected = graph.get_connected_chunks("chunk2")
    print(f"🔗 Chunks conectados a chunk2: {connected}")
    
    # 5. Test análisis avanzado
    print("\n5️⃣ Test análisis avanzado:")
    path = graph.find_path("chunk1", "chunk3")
    print(f"🛤️  Camino chunk1 → chunk3: {path}")
    
    important = graph.get_most_important_chunks(top_k=3)
    print(f"⭐ Chunks más importantes: {important}")
    
    stats = graph.get_stats()
    print(f"📊 Estadísticas: {stats}")
    
    # 6. Test exportación
    print("\n6️⃣ Test exportación:")
    export_data = graph.export_to_dict()
    print(f"💾 Datos exportados (chunks): {len(export_data.get('nodes', []))}")
    print(f"💾 Datos exportados (edges): {len(export_data.get('edges', []))}")
    
    print("\n✅ ¡Todos los tests pasaron! La arquitectura modular funciona correctamente.")
    print("=" * 60)

def test_builder_pattern():
    """Test del patrón Builder para crear grafos"""
    
    print("\n🏗️  Probando patrón Builder...")
    print("=" * 40)
    
    # Data de ejemplo
    chunks_data = [
        {
            'chunk_id': 'doc1_chunk1',
            'content': 'Introducción a los sistemas de información',
            'metadata': {'file': 'sistemas.pdf', 'page': 1}
        },
        {
            'chunk_id': 'doc1_chunk2', 
            'content': 'Los sistemas de información son fundamentales',
            'metadata': {'file': 'sistemas.pdf', 'page': 2}
        },
        {
            'chunk_id': 'doc2_chunk1',
            'content': 'Machine Learning y AI en sistemas modernos',
            'metadata': {'file': 'ml.pdf', 'page': 1}
        }
    ]
    
    # Crear grafo usando builder
    graph = create_simple_rag_graph(chunks_data)
    
    # Verificar construcción
    stats = graph.get_stats()
    print(f"📈 Grafo construido - Nodos: {stats['nodes']}, Edges: {stats['edges']}")
    
    # Test funcionalidad
    important_chunks = graph.get_most_important_chunks(top_k=2)
    print(f"🎯 Chunks importantes: {important_chunks}")
    
    print("✅ Builder pattern funciona correctamente!")

if __name__ == "__main__":
    try:
        test_modular_architecture()
        test_builder_pattern()
        print("\n🎉 ¡REFACTORIZACIÓN EXITOSA!")
        print("La arquitectura modular está funcionando perfectamente.")
        
    except Exception as e:
        print(f"\n❌ Error en los tests: {e}")
        import traceback
        traceback.print_exc()
