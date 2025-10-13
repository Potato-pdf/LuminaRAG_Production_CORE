#!/usr/bin/env python3
"""
🧪 SCRIPT DE PRUEBA PARA LA API REST
====================================

Prueba los diferentes endpoints de la API para verificar su funcionamiento.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuración
API_BASE_URL = "http://localhost:8000"
API_V1 = f"{API_BASE_URL}/api/v1"


def print_section(title: str):
    """Imprimir sección con formato"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_response(response: requests.Response):
    """Imprimir respuesta formateada"""
    print(f"\nStatus: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.text}")


def test_root():
    """Probar endpoint raíz"""
    print_section("TEST 1: Endpoint Raíz")
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_health():
    """Probar health check"""
    print_section("TEST 2: Health Check")
    
    try:
        response = requests.get(f"{API_V1}/health")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Estado: {data['status']}")
            print(f"✅ FAISS cargado: {data['faiss_loaded']}")
            print(f"✅ LLM conectado: {data['llm_connected']}")
            return data['status'] == 'healthy'
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_stats():
    """Probar estadísticas"""
    print_section("TEST 3: Estadísticas del Sistema")
    
    try:
        response = requests.get(f"{API_V1}/stats")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Documentos: {data['total_documents']}")
            print(f"📊 Chunks: {data['total_chunks']}")
            print(f"📊 Raíces indexadas: {data['indexed_roots']}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_documents():
    """Probar listado de documentos"""
    print_section("TEST 4: Listar Documentos")
    
    try:
        response = requests.get(f"{API_V1}/documents")
        print_response(response)
        
        if response.status_code == 200:
            documents = response.json()
            print(f"\n📚 Total documentos: {len(documents)}")
            for doc in documents[:3]:  # Mostrar primeros 3
                print(f"\n  • {doc['document_id']}")
                print(f"    Raíz: {doc['root_chunk_id']}")
                print(f"    Chunks: {doc['total_chunks']}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_query_simple():
    """Probar consulta simple"""
    print_section("TEST 5: Consulta Simple")
    
    query_data = {
        "query": "¿De qué trata este documento?",
        "k": 3,
        "k_roots": 3,
        "include_context": False
    }
    
    try:
        print(f"\n📝 Enviando consulta: {query_data['query']}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_V1}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        elapsed_time = time.time() - start_time
        
        print(f"⏱️ Tiempo de respuesta HTTP: {elapsed_time:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Consulta: {data['query']}")
            print(f"\n🤖 RESPUESTA:")
            print("-" * 60)
            print(data['answer'])
            print("-" * 60)
            
            print(f"\n📊 Chunks relevantes: {len(data['chunks'])}")
            for i, chunk in enumerate(data['chunks'], 1):
                print(f"\n  {i}. Score: {chunk['score']:.4f} | Doc: {chunk['document']}")
                preview = chunk['content'][:100] + "..." if len(chunk['content']) > 100 else chunk['content']
                print(f"     {preview}")
            
            print(f"\n📚 Documentos usados: {', '.join(data['documents_used'])}")
            print(f"⏱️ Tiempo procesamiento: {data['processing_time']:.2f}s")
            
            return True
        else:
            print_response(response)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_query_complex():
    """Probar consulta compleja con contexto"""
    print_section("TEST 6: Consulta con Contexto")
    
    query_data = {
        "query": "¿Cuáles son los procedimientos más importantes mencionados?",
        "k": 5,
        "k_roots": 5,
        "include_context": True
    }
    
    try:
        print(f"\n📝 Enviando consulta: {query_data['query']}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_V1}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        elapsed_time = time.time() - start_time
        
        print(f"⏱️ Tiempo de respuesta HTTP: {elapsed_time:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n🤖 RESPUESTA:")
            print("-" * 60)
            print(data['answer'][:500] + "..." if len(data['answer']) > 500 else data['answer'])
            print("-" * 60)
            
            print(f"\n📊 Chunks: {len(data['chunks'])} | Docs: {len(data['documents_used'])}")
            print(f"⏱️ Tiempo: {data['processing_time']:.2f}s")
            
            return True
        else:
            print_response(response)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_invalid_query():
    """Probar consulta inválida"""
    print_section("TEST 7: Validación de Entrada")
    
    # Consulta vacía
    try:
        response = requests.post(
            f"{API_V1}/query",
            json={"query": ""},  # Consulta vacía (inválida)
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 422:  # Validation error
            print("✅ Validación correcta: rechaza consulta vacía")
            return True
        else:
            print(f"⚠️ Se esperaba error 422, recibido {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Ejecutar todos los tests"""
    print("🧪 PRUEBAS DE LA API REST LUMINA RAG")
    print("=" * 60)
    
    print(f"\n🌐 API Base URL: {API_BASE_URL}")
    print(f"📡 API Version: v1")
    
    # Verificar que el servidor esté corriendo
    try:
        requests.get(API_BASE_URL, timeout=2)
    except:
        print("\n❌ ERROR: El servidor API no está corriendo")
        print("💡 Iniciar con: python3 api_server.py")
        return
    
    # Ejecutar tests
    tests = [
        ("Endpoint Raíz", test_root),
        ("Health Check", test_health),
        ("Estadísticas", test_stats),
        ("Listar Documentos", test_documents),
        ("Consulta Simple", test_query_simple),
        ("Consulta con Contexto", test_query_complex),
        ("Validación de Entrada", test_invalid_query)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            time.sleep(0.5)  # Pequeña pausa entre tests
        except Exception as e:
            print(f"\n❌ Error en {name}: {e}")
            results.append((name, False))
    
    # Resumen
    print_section("RESUMEN DE PRUEBAS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
    else:
        print(f"⚠️ {total - passed} tests fallaron")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
