#!/usr/bin/env python3
"""
🔍 SISTEMA DE CONSULTAS SIMPLIFICADO
===================================

Sistema simplificado que usa directamente el grafo y Ollama para consultas.
"""

import os
import pickle
import json
from typing import List, Dict
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

def simple_query_system():
    """Sistema de consultas simplificado"""
    
    from llama_index.llms.ollama import Ollama
    from src.config import OLLAMA_CONFIG, STORAGE_CONFIG
    
    print("🔍 SISTEMA RAG SIMPLIFICADO")
    print("="*40)
    
    # 1. Cargar grafo
    print("🕸️ Cargando grafo...")
    graph_path = STORAGE_CONFIG["graph_path"]
    try:
        with open(graph_path, 'rb') as f:
            document_graph = pickle.load(f)
        
        stats = document_graph.get_stats()
        print(f"✅ Grafo cargado - Nodos: {stats['nodes']}, Conexiones: {stats['edges']}")
    except Exception as e:
        print(f"❌ Error cargando grafo: {e}")
        return False
    
    # 2. Configurar Ollama
    print("🤖 Configurando Ollama...")
    try:
        llm = Ollama(
            model=OLLAMA_CONFIG["model"],
            base_url=OLLAMA_CONFIG["base_url"],
            temperature=0.1,
            request_timeout=120.0
        )
        
        # Test simple
        test_response = llm.complete("¿Funciona?")
        print(f"✅ Ollama funcionando: {str(test_response)[:50]}...")
        
    except Exception as e:
        print(f"❌ Error con Ollama: {e}")
        return False
    
    # 3. Función de consulta
    def query_with_graph(question: str) -> str:
        """Hacer consulta usando el grafo"""
        print(f"\n🔍 Consulta: {question}")
        
        # Obtener chunks más importantes del grafo
        important_chunks = document_graph.get_most_important_chunks(top_k=5)
        
        # Construir contexto
        context = "Contexto del documento:\n\n"
        for chunk_id, importance in important_chunks:
            content = document_graph.get_chunk_content(chunk_id)
            if content:
                context += f"[Relevancia: {importance:.3f}] {content[:500]}\n\n"
        
        # Construir prompt
        prompt = f"""
Basándote en el siguiente contexto del documento, responde la pregunta de manera detallada y explícita.

{context}

Pregunta: {question}

Respuesta detallada:
"""
        
        print("🤖 Consultando a Ollama...")
        try:
            response = llm.complete(prompt)
            return str(response)
        except Exception as e:
            return f"Error en consulta: {e}"
    
    # 4. Modo interactivo
    print("\n🎯 MODO INTERACTIVO")
    print("="*40)
    print("💡 Escribe 'quit' para salir")
    
    while True:
        try:
            question = input("\n🤔 Tu pregunta: ").strip()
            
            if question.lower() in ['quit', 'exit', 'salir']:
                print("👋 ¡Hasta luego!")
                break
            
            if not question:
                print("⚠️ Por favor ingresa una pregunta")
                continue
            
            # Hacer consulta
            answer = query_with_graph(question)
            
            print("\n" + "="*60)
            print("💬 RESPUESTA")
            print("="*60)
            print(answer)
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    return True

if __name__ == "__main__":
    simple_query_system()