#!/usr/bin/env python3
"""
Script para probar el procesamiento de documentos con LlamaParse.
Útil para verificar que funciona correctamente antes de integrarlo en el flujo RAG.
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

def main():
    """Prueba el procesamiento de documentos con LlamaParse"""
    
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("ERROR: LLAMA_CLOUD_API_KEY no está configurada en el archivo .env")
        print("Por favor, configura esta variable con tu API key de LlamaParse")
        return
    
    print("Probando LlamaParse para procesar documentos...")
    
    # Procesar documentos
    documents = parse_documents(
        directory_path="pdfs",  # Carpeta donde están los PDFs
        api_key=api_key
    )
    
    if not documents:
        print("No se procesaron documentos. Verifica que existan archivos PDF en la carpeta 'pdfs'")
        return
    
    print(f"\nSe procesaron {len(documents)} documentos")
    
    # Mostrar información de los documentos
    for i, doc in enumerate(documents):
        print(f"\n--- Documento {i+1} ---")
        print(f"ID: {doc.doc_id}")
        print(f"Metadata: {json.dumps(doc.metadata, indent=2)}")
        print(f"Texto (primeros 300 caracteres): {doc.text[:300]}...")

if __name__ == "__main__":
    main()
