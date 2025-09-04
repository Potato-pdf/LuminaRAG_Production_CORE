#!/usr/bin/env python3
"""
Script para probar diferentes configuraciones de chunking y preparar 
el terreno para la implementación del DGA (Document Graph Augmentation).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import sys
import json

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno
load_dotenv()

from src.parse_docs import parse_documents
from src.embedding.multilingual import choice_embedding
from src.create_index.create_index_llamaindex import create_index_llamaindex
from src.model_ai import connect_ollama

def main():
    """Prueba diferentes configuraciones de chunking"""
    
    # Verificar API key
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("ERROR: No se encontró API key en el archivo .env")
        print("Por favor, configura LLAMA_CLOUD_API_KEY o LLAMA_API_KEY con tu API key de LlamaParse")
        return
    
    # Procesar documentos con LlamaParse
    print("Procesando documentos con LlamaParse...")
    documents = parse_documents(
        directory_path="pdfs",
        api_key=api_key
    )
    
    if not documents:
        print("No se procesaron documentos. Verifica que existan archivos PDF en la carpeta 'pdfs'")
        return
    
    print(f"Se procesaron {len(documents)} documentos")
    
    # Cargar modelo de embedding
    print("\nCargando modelo de embedding...")
    embedding_model = choice_embedding()
    
    # Configuraciones de chunking a probar
    chunking_configs = [
        {"chunk_size": 512, "chunk_overlap": 100, "chunk_window_size": 2},
        {"chunk_size": 1024, "chunk_overlap": 200, "chunk_window_size": 3},
        {"chunk_size": 2048, "chunk_overlap": 400, "chunk_window_size": 5}
    ]
    
    # Probar diferentes configuraciones
    print("\n--- Probando diferentes configuraciones de chunking ---")
    
    results = []
    for config in chunking_configs:
        print(f"\nProbando configuración: {config}")
        
        # Crear índice con esta configuración
        index = create_index_llamaindex(
            documents=documents,
            vector_store=None,  # No usamos Milvus para esta prueba
            embed_model=embedding_model,
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
            chunk_window_size=config["chunk_window_size"]
        )
        
        # Guardar resultados
        result = {
            "config": config,
            "index_stats": {
                "num_nodes": len(index.index_struct.nodes_dict)
            }
        }
        results.append(result)
    
    # Mostrar resultados comparativos
    print("\n--- Resultados comparativos ---")
    for result in results:
        config = result["config"]
        stats = result["index_stats"]
        print(f"Config: chunk_size={config['chunk_size']}, overlap={config['chunk_overlap']}, window={config['chunk_window_size']}")
        print(f"Número de chunks/nodos: {stats['num_nodes']}")
        print("-" * 50)
    
    print("\nEsta información te ayudará a decidir la mejor configuración para tu implementación DGA.")

if __name__ == "__main__":
    main()
