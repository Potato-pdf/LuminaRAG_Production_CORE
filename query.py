#!/usr/bin/env python3
"""
🌳 SISTEMA DE CONSULTAS JERÁRQUICO
==================================

Sistema de consultas avanzado que aprovecha la arquitectura jerárquica:
- PageRank jerárquico con múltiples estrategias
- Contexto intra-documento e inter-documento
- Búsquedas especializadas por nivel del árbol
- Respuestas enriquecidas con información jerárquica
"""

import os
import pickle
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

def main():
    """Sistema de consultas jerárquico principal"""
    
    from llama_index.llms.ollama import Ollama
    from src.config import OLLAMA_CONFIG, STORAGE_CONFIG
    
    print("🌳 SISTEMA RAG JERÁRQUICO LUMINA")
    print("="*50)
    
    # 1. Cargar grafo jerárquico
    print("🕸️ Cargando arquitectura jerárquica...")
    hierarchical_graph = load_hierarchical_graph()
    if not hierarchical_graph:
        return False
    
    # 2. Configurar Ollama
    print("🤖 Configurando Ollama...")
    llm = setup_ollama()
    if not llm:
        return False
    
    # 3. Crear sistema de consultas jerárquico
    query_system = HierarchicalQuerySystem(hierarchical_graph, llm)
    
    # 4. Modo interactivo
    query_system.interactive_mode()
    
    return True

def load_hierarchical_graph():
    """Cargar grafo jerárquico desde almacenamiento"""
    from src.config import STORAGE_CONFIG
    
    hierarchical_graph_path = STORAGE_CONFIG["graph_path"].replace(".pkl", "_hierarchical.pkl")
    
    try:
        with open(hierarchical_graph_path, 'rb') as f:
            hierarchical_graph = pickle.load(f)
        
        if hierarchical_graph.is_hierarchical:
            stats = hierarchical_graph.get_hierarchical_stats()
            print(f"✅ Grafo jerárquico cargado:")
            print(f"   📄 Documentos: {stats['documents_count']}")
            print(f"   🌿 Raíces: {stats['document_roots']}")
            print(f"   🔗 Total chunks: {stats['total_chunks']}")
            return hierarchical_graph
        else:
            print("❌ El grafo cargado no es jerárquico")
            return None
            
    except Exception as e:
        print(f"❌ Error cargando grafo jerárquico: {e}")
        return None

def setup_ollama():
    """Configurar y probar Ollama"""
    from llama_index.llms.ollama import Ollama
    from src.config import OLLAMA_CONFIG
    
    try:
        llm = Ollama(
            model=OLLAMA_CONFIG["model"],
            base_url=OLLAMA_CONFIG["base_url"],
            temperature=0.1,
            request_timeout=120.0
        )
        
        # Test de conectividad
        test_response = llm.complete("Test")
        print(f"✅ Ollama funcionando: {str(test_response)[:30]}...")
        return llm
        
    except Exception as e:
        print(f"❌ Error con Ollama: {e}")
        return None

class HierarchicalQuerySystem:
    """Sistema de consultas que aprovecha la arquitectura jerárquica"""
    
    def __init__(self, hierarchical_graph, llm):
        self.graph = hierarchical_graph
        self.llm = llm
        self.query_strategies = {
            '1': ('mixed', 'Estrategia mixta (recomendada)'),
            '2': ('roots_first', 'Priorizar raíces de documentos'),
            '3': ('within_docs', 'Distribuido por documentos'),
            '4': ('meta_only', 'Solo meta-grafo (raíces)')
        }
    
    def interactive_mode(self):
        """Modo interactivo de consultas"""
        print("\n🌳 MODO INTERACTIVO JERÁRQUICO")
        print("="*50)
        print("💡 Comandos especiales:")
        print("   📊 'stats' - Estadísticas del grafo")
        print("   🌿 'docs' - Listar documentos")
        print("   ⚙️ 'strategy' - Cambiar estrategia de búsqueda")
        print("   🚪 'quit' - Salir")
        print()
        
        current_strategy = 'mixed'
        
        while True:
            try:
                question = input(f"\n🤔 Pregunta [{current_strategy}]: ").strip()
                
                if question.lower() in ['quit', 'exit', 'salir']:
                    print("👋 ¡Hasta luego!")
                    break
                
                if question.lower() == 'stats':
                    self.show_stats()
                    continue
                
                if question.lower() == 'docs':
                    self.show_documents()
                    continue
                
                if question.lower() == 'strategy':
                    current_strategy = self.select_strategy()
                    continue
                
                if not question:
                    print("⚠️ Por favor ingresa una pregunta")
                    continue
                
                # Procesar consulta jerárquica
                answer = self.hierarchical_query(question, current_strategy)
                
                print(f"\n" + "="*80)
                print("💬 RESPUESTA JERÁRQUICA")
                print("="*80)
                print(answer)
                print("="*80)
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def hierarchical_query(self, question: str, strategy: str = 'mixed') -> str:
        """Realizar consulta usando arquitectura jerárquica"""
        print(f"\n🔍 Procesando consulta con estrategia '{strategy}'...")
        
        # 1. Obtener chunks importantes usando estrategia jerárquica
        important_chunks = self.graph.get_most_important_chunks_hierarchical(
            top_k=8, strategy=strategy
        )
        
        # 2. Construir contexto jerárquico enriquecido
        context = self.build_hierarchical_context(important_chunks, question)
        
        # 3. Generar respuesta con Ollama
        prompt = self.build_hierarchical_prompt(context, question)
        
        print("🤖 Generando respuesta jerárquica...")
        try:
            response = self.llm.complete(prompt)
            return str(response)
        except Exception as e:
            return f"Error generando respuesta: {e}"
    
    def build_hierarchical_context(self, important_chunks: List, question: str) -> Dict[str, Any]:
        """Construir contexto jerárquico enriquecido"""
        context = {
            'primary_chunks': [],
            'document_contexts': {},
            'cross_document_info': [],
            'hierarchy_info': []
        }
        
        # Procesar chunks importantes
        for chunk_id, score, doc_name in important_chunks:
            chunk_content = self.graph.get_chunk_content(chunk_id)
            if not chunk_content:
                continue
            
            # Información del chunk principal
            chunk_info = {
                'id': chunk_id,
                'content': chunk_content[:800],  # Limitar tamaño
                'score': round(score, 3),
                'document': doc_name
            }
            context['primary_chunks'].append(chunk_info)
            
            # Contexto del documento
            if doc_name not in context['document_contexts']:
                doc_context = self.graph.get_document_context(chunk_id, context_size=2)
                context['document_contexts'][doc_name] = []
                
                for context_chunk in doc_context:
                    context_content = self.graph.get_chunk_content(context_chunk)
                    if context_content:
                        context['document_contexts'][doc_name].append({
                            'id': context_chunk,
                            'content': context_content[:400]
                        })
        
        # Información jerárquica adicional
        document_roots = self.graph.get_document_roots()
        for doc_name, root_chunk in document_roots.items():
            root_content = self.graph.get_chunk_content(root_chunk)
            if root_content:
                context['hierarchy_info'].append({
                    'document': doc_name,
                    'root_content': root_content[:300],
                    'is_root': True
                })
        
        return context
    
    def build_hierarchical_prompt(self, context: Dict[str, Any], question: str) -> str:
        """Construir prompt jerárquico optimizado"""
        prompt = f"""Basándote en la información jerárquica de documentos, responde la pregunta de manera detallada.

INFORMACIÓN PRINCIPAL (chunks más relevantes):
"""
        
        # Chunks principales
        for i, chunk in enumerate(context['primary_chunks'], 1):
            prompt += f"\n{i}. [{chunk['document']}] (Relevancia: {chunk['score']})\n"
            prompt += f"   {chunk['content']}\n"
        
        # Contexto por documento
        if context['document_contexts']:
            prompt += f"\nCONTEXTO ADICIONAL POR DOCUMENTO:\n"
            for doc_name, doc_chunks in context['document_contexts'].items():
                prompt += f"\n📄 {doc_name}:\n"
                for chunk in doc_chunks[:2]:  # Limitar contexto
                    prompt += f"   • {chunk['content'][:200]}...\n"
        
        # Información de raíces
        if context['hierarchy_info']:
            prompt += f"\nINFORMACIÓN DE RAÍCES DE DOCUMENTOS:\n"
            for root_info in context['hierarchy_info']:
                prompt += f"\n🌿 {root_info['document']} (Raíz):\n"
                prompt += f"   {root_info['root_content']}\n"
        
        prompt += f"""
PREGUNTA: {question}

INSTRUCCIONES:
- Usa la información jerárquica para dar una respuesta completa
- Menciona qué documentos específicos contienen la información relevante
- Si la información viene de raíces de documentos, indica su importancia
- Sé específico y detallado en tu respuesta

RESPUESTA:"""
        
        return prompt
    
    def show_stats(self):
        """Mostrar estadísticas del grafo jerárquico"""
        stats = self.graph.get_hierarchical_stats()
        
        print(f"\n📊 ESTADÍSTICAS JERÁRQUICAS")
        print("="*40)
        print(f"📄 Documentos: {stats['documents_count']}")
        print(f"🌿 Raíces: {stats['document_roots']}")
        print(f"📊 Total chunks: {stats['total_chunks']}")
        print(f"🔗 Conexiones: {stats['total_connections']}")
        print(f"🌐 Meta-conexiones: {stats['meta_graph_connections']}")
        print(f"📈 Conectividad cruzada: {stats.get('cross_document_connectivity', 0):.2%}")
        
        if 'document_tree_depths' in stats:
            print(f"\n🌳 PROFUNDIDAD DE ÁRBOLES:")
            for doc, depth in stats['document_tree_depths'].items():
                print(f"   📄 {doc}: {depth} niveles")
    
    def show_documents(self):
        """Mostrar información de documentos"""
        documents = self.graph.get_documents_list()
        document_roots = self.graph.get_document_roots()
        
        print(f"\n📄 DOCUMENTOS EN EL SISTEMA")
        print("="*40)
        
        for doc_name in documents:
            chunks_count = len(self.graph.get_chunks_by_document(doc_name))
            root_chunk = document_roots.get(doc_name, 'N/A')
            tree_stats = self.graph.get_document_tree_stats(doc_name)
            
            print(f"\n📄 {doc_name}")
            print(f"   🌿 Raíz: {root_chunk}")
            print(f"   📊 Chunks: {chunks_count}")
            print(f"   📏 Profundidad: {tree_stats.get('tree_depth', 0)}")
            print(f"   🔗 Conexiones: {tree_stats.get('tree_edges', 0)}")
    
    def select_strategy(self) -> str:
        """Seleccionar estrategia de búsqueda"""
        print(f"\n⚙️ ESTRATEGIAS DE BÚSQUEDA DISPONIBLES:")
        print("="*40)
        
        for key, (strategy, description) in self.query_strategies.items():
            print(f"{key}. {description}")
        
        while True:
            try:
                choice = input("\nSelecciona estrategia (1-4): ").strip()
                if choice in self.query_strategies:
                    strategy, description = self.query_strategies[choice]
                    print(f"✅ Estrategia seleccionada: {description}")
                    return strategy
                else:
                    print("❌ Opción inválida")
            except KeyboardInterrupt:
                return 'mixed'  # Default

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error en sistema de consultas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)