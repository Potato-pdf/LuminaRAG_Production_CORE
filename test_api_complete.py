#!/usr/bin/env python3
"""
🧪 SCRIPT DE PRUEBA PARA LA API LUMINA RAG
==========================================

Prueba los endpoints de indexación y consulta por empresa.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"

def test_health():
    """Probar health check"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check OK")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_index_documents(empresa: str, private: bool):
    """Probar indexación de documentos"""
    print(f"📥 Indexando documentos para {empresa} ({'privado' if private else 'público'})...")

    payload = {
        "empresa": empresa,
        "titulo": f"Test document for {empresa}",
        "private": private
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/index",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Indexación exitosa: {result['documents_processed']} documentos, {result['chunks_created']} chunks")
            print(f"   📂 Colección: {result['milvus_collection']}")
            return True
        else:
            print(f"❌ Error en indexación: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en indexación: {e}")
        return False

def test_query_public(empresa: str, query: str):
    """Probar consulta de documentos públicos"""
    print(f"🔍 Consultando documentos públicos de {empresa}...")

    payload = {
        "query": query,
        "k": 3
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/query/public/{empresa}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Consulta pública exitosa")
            print(f"   📝 Respuesta: {result['answer'][:100]}...")
            print(f"   📊 Chunks encontrados: {len(result['chunks'])}")
            return True
        else:
            print(f"❌ Error en consulta pública: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en consulta pública: {e}")
        return False

def test_query_private(empresa: str, query: str):
    """Probar consulta de documentos privados"""
    print(f"🔒 Consultando documentos privados de {empresa}...")

    payload = {
        "query": query,
        "k": 3
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/query/private/{empresa}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Consulta privada exitosa")
            print(f"   📝 Respuesta: {result['answer'][:100]}...")
            print(f"   📊 Chunks encontrados: {len(result['chunks'])}")
            return True
        else:
            print(f"❌ Error en consulta privada: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en consulta privada: {e}")
        return False

def main():
    """Ejecutar pruebas completas"""
    print("🧪 PRUEBAS DE API LUMINA RAG")
    print("="*50)

    # 1. Health check
    if not test_health():
        print("❌ API no está disponible. Abortando pruebas.")
        return

    # 2. Indexar documentos públicos para FINFERSSA
    if test_index_documents("FINFERSSA", False):
        time.sleep(2)  # Esperar a que se complete la indexación

        # 3. Probar consulta de documentos públicos
        test_query_public("FINFERSSA", "¿Qué información hay sobre contratos?")

    # 4. Indexar documentos privados para FINFERSSA
    if test_index_documents("FINFERSSA", True):
        time.sleep(2)  # Esperar a que se complete la indexación

        # 5. Probar consulta de documentos privados
        test_query_private("FINFERSSA", "¿Qué información confidencial hay?")

    print("\n🎉 Pruebas completadas!")
    print("📚 Documentación completa: http://localhost:8000/docs")

if __name__ == "__main__":
    main()