#!/usr/bin/env python3
"""
Script de prueba para el sistema FAISS RAG
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_faiss import FAISSQuerySystem

def test_query(query_text):
    """Prueba una consulta en el sistema FAISS"""
    try:
        # Inicializar sistema
        rag_system = FAISSQuerySystem()

        print("🔍 Probando consulta:", query_text)
        print("-" * 50)

        # Realizar búsqueda
        results = rag_system.search(query_text, k=3)

        print(f"📊 Resultados encontrados: {len(results)}")
        print()

        for i, result in enumerate(results, 1):
            print(f"🔸 Resultado {i}:")
            print(f"   📄 Documento: {result.get('document_name', 'N/A')}")
            print(f"   📊 Score: {result.get('score', 'N/A'):.4f}")
            print(f"   📝 Contenido: {result.get('content', 'N/A')[:200]}...")
            print()

        # Generar respuesta con LLM
        print("🤖 Generando respuesta con LLM...")
        response = rag_system.generate_response(query_text, results)
        print("💬 Respuesta:")
        print(response)

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "¿Qué es el dedo de momia?"

    test_query(query)