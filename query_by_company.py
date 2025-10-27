#!/usr/bin/env python3
"""
🔍 CONSULTAS POR EMPRESA Y PRIVACIDAD
=====================================

Sistema de consultas que permite buscar documentos filtrados por:
- Empresa específica
- Tipo de documento (público/privado)
- Combinaciones de ambos
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

def main():
    """Sistema de consultas por empresa y privacidad"""

    print("🔍 CONSULTAS POR EMPRESA LUMINA")
    print("="*50)

    # 1. Listar colecciones disponibles
    collections = list_available_collections()
    if not collections:
        print("❌ No se encontraron colecciones indexadas")
        return

    print(f"📂 Colecciones disponibles: {len(collections)}")
    for i, collection in enumerate(collections, 1):
        print(f"   {i}. {collection}")

    # 2. Seleccionar colección
    selected_collection = select_collection(collections)
    if not selected_collection:
        return

    # 3. Cargar sistema de consulta para la colección
    query_system = load_query_system_for_collection(selected_collection)
    if not query_system:
        print(f"❌ Error cargando sistema para colección {selected_collection}")
        return

    # 4. Bucle de consultas
    while True:
        print(f"\n🔍 Consultando colección: {selected_collection}")
        query = input("💬 Ingrese su consulta (o 'exit' para salir): ").strip()

        if query.lower() in ['exit', 'quit', 'q']:
            break

        if not query:
            continue

        # Realizar consulta
        results = perform_query(query_system, query, selected_collection)

        # Mostrar resultados
        display_results(results, selected_collection)

def list_available_collections() -> List[str]:
    """Listar colecciones disponibles en el sistema FAISS"""
    from src.config import STORAGE_CONFIG

    faiss_dir = Path(STORAGE_CONFIG["base_dir"]) / "faiss_collections"
    if not faiss_dir.exists():
        return []

    collections = []
    for faiss_file in faiss_dir.glob("*.faiss"):
        collection_name = faiss_file.stem  # Nombre sin extensión
        collections.append(collection_name)

    return sorted(collections)

def select_collection(collections: List[str]) -> Optional[str]:
    """Permitir al usuario seleccionar una colección"""
    if len(collections) == 1:
        collection = collections[0]
        print(f"📂 Usando colección única: {collection}")
        return collection

    while True:
        try:
            choice = input(f"\n🔢 Seleccione colección (1-{len(collections)}) o 'list' para ver todas: ").strip()

            if choice.lower() == 'list':
                print("\n📂 Colecciones disponibles:")
                for i, collection in enumerate(collections, 1):
                    print(f"   {i}. {collection}")
                continue

            idx = int(choice) - 1
            if 0 <= idx < len(collections):
                return collections[idx]
            else:
                print(f"❌ Selección inválida. Use 1-{len(collections)}")

        except ValueError:
            print("❌ Ingrese un número válido")

def load_query_system_for_collection(collection_name: str):
    """Cargar sistema de consulta FAISS para una colección específica"""
    try:
        from src.config import STORAGE_CONFIG, EMBEDDING_CONFIG
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        import faiss

        faiss_dir = Path(STORAGE_CONFIG["base_dir"]) / "faiss_collections"
        faiss_path = faiss_dir / f"{collection_name}.faiss"
        metadata_path = faiss_dir / f"{collection_name}_metadata.json"

        if not faiss_path.exists():
            print(f"❌ Archivo FAISS no encontrado: {faiss_path}")
            return None

        # Cargar índice FAISS
        faiss_index = faiss.read_index(str(faiss_path))
        print(f"✅ Índice FAISS cargado: {faiss_path}")

        # Cargar metadata
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f"✅ Metadata cargada: {len(metadata.get('documents', []))} documentos")
        else:
            metadata = {"documents": []}
            print("⚠️ Metadata no encontrada, usando datos básicos")

        # Configurar embedding
        embedding_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_CONFIG["model_name"],
            max_length=512,
            device="cpu"
        )

        return {
            'faiss_index': faiss_index,
            'embedding_model': embedding_model,
            'metadata': metadata,
            'collection_name': collection_name
        }

    except Exception as e:
        print(f"❌ Error cargando sistema de consulta: {e}")
        return None

def perform_query(query_system: Dict, query: str, collection_name: str, top_k: int = 5):
    """Realizar consulta en el sistema FAISS"""
    try:
        faiss_index = query_system['faiss_index']
        embedding_model = query_system['embedding_model']
        metadata = query_system['metadata']

        # Generar embedding de la consulta
        query_embedding = embedding_model.get_text_embedding(query)
        if len(query_embedding) != faiss_index.d:
            print(f"❌ Dimensión de embedding incorrecta: {len(query_embedding)} vs {faiss_index.d}")
            return []

        # Convertir a numpy array
        import numpy as np
        query_vector = np.array([query_embedding], dtype=np.float32)

        # Buscar en FAISS
        distances, indices = faiss_index.search(query_vector, top_k)

        # Preparar resultados
        results = []
        documents = metadata.get('documents', [])

        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(documents) and idx >= 0:
                doc_info = documents[idx]
                results.append({
                    'rank': i + 1,
                    'score': float(1 / (1 + distance)),  # Convertir distancia a similitud
                    'distance': float(distance),
                    'document': doc_info,
                    'collection': collection_name
                })

        return results

    except Exception as e:
        print(f"❌ Error en consulta: {e}")
        return []

def display_results(results: List[Dict], collection_name: str):
    """Mostrar resultados de la consulta"""
    if not results:
        print("❌ No se encontraron resultados")
        return

    print(f"\n📊 RESULTADOS PARA COLECCIÓN: {collection_name}")
    print("="*80)

    for result in results:
        doc = result['document']
        print(f"📄 Documento: {doc.get('file_name', 'unknown')}")
        print(f"🏢 Empresa: {doc.get('empresa', 'unknown')}")
        print(f"🔒 Privacidad: {'Privado' if doc.get('private', False) else 'Público'}")
        print(f"🎯 Score: {result['score']:.4f}")
        print(f"📏 Distancia: {result['distance']:.4f}")
        print("-"*50)

    print(f"✅ {len(results)} resultados encontrados")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Consultas finalizadas")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error en consultas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)