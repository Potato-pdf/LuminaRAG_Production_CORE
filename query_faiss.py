#!/usr/bin/env python3
"""
🔍 SISTEMA DE CONSULTAS CON FAISS
=================================

Sistema de consultas optimizado que usa FAISS para encontrar raíces relevantes
y luego busca específicamente en esos árboles jerárquicos.

Flujo optimizado:
1. FAISS encuentra las 5 raíces más similares a la query
2. Búsqueda en esos árboles específicos
3. Combinación inteligente de scores
4. Respuesta contextualizada
"""

import os
import sys
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

def main():
    """Sistema de consultas FAISS principal"""
    
    print("🚀 SISTEMA RAG FAISS-GPU + ÁRBOLES JERÁRQUICOS")
    print("=" * 60)
    
    # 1. Cargar sistema FAISS
    print("📂 Cargando sistema FAISS...")
    faiss_system = load_faiss_system()
    if not faiss_system:
        return False
    
    # 2. Configurar Ollama
    print("🤖 Configurando Ollama...")
    llm = setup_ollama()
    if not llm:
        return False
    
    # 3. Crear sistema de consultas FAISS
    query_system = FAISSQuerySystem(faiss_system, llm)
    
    # 4. Modo interactivo
    query_system.interactive_mode()
    
    return True


def load_faiss_system():
    """Cargar sistema FAISS"""
    try:
        from src.FAISS.faiss_integration import load_faiss_system
        return load_faiss_system()
    except Exception as e:
        print(f"❌ Error cargando sistema FAISS: {e}")
        print("💡 Ejecutar primero: python3 migrate_to_faiss.py")
        return None


def setup_ollama():
    """Configurar conexión con Ollama"""
    try:
        from src.model_ai.choice_model_llama import connect_ollama
        from src.config import OLLAMA_CONFIG
        
        llm = connect_ollama()
        print(f"✅ Ollama conectado: {OLLAMA_CONFIG['model']}")
        return llm
        
    except Exception as e:
        print(f"❌ Error conectando Ollama: {e}")
        return None


class FAISSQuerySystem:
    """Sistema de consultas optimizado con FAISS"""
    
    def __init__(self, faiss_system, llm):
        self.faiss_system = faiss_system
        self.llm = llm
        self.session_history = []
        
    def interactive_mode(self):
        """Modo interactivo de consultas"""
        
        print("\n🌟 MODO INTERACTIVO FAISS RAG")
        print("-" * 40)
        print("Comandos especiales:")
        print("  'exit' / 'quit' - Salir")
        print("  'stats' - Estadísticas del sistema")
        print("  'docs' - Lista de documentos")
        print("  'help' - Ayuda")
        print("  'test [query]' - Prueba de búsqueda sin LLM")
        print("-" * 40)
        
        while True:
            try:
                query = input("\n🔍 Tu consulta: ").strip()
                
                if not query:
                    continue
                    
                # Comandos especiales
                if query.lower() in ['exit', 'quit', 'salir']:
                    print("👋 ¡Hasta luego!")
                    break
                elif query.lower() == 'stats':
                    self._show_stats()
                    continue
                elif query.lower() == 'docs':
                    self._show_documents()
                    continue
                elif query.lower() == 'help':
                    self._show_help()
                    continue
                elif query.lower().startswith('test '):
                    test_query = query[5:].strip()
                    self._test_search(test_query)
                    continue
                
                # Procesar consulta normal
                response = self.process_query(query)
                print(f"\n🤖 {response}")
                
                # Agregar a historial
                self.session_history.append({
                    'query': query,
                    'response': response
                })
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def process_query(self, query: str, k: int = 5, k_roots: int = 5) -> str:
        """
        Procesar una consulta completa
        
        Args:
            query: Consulta del usuario
            k: Número de chunks para el contexto
            k_roots: Número de raíces a considerar
            
        Returns:
            Respuesta generada por el LLM
        """
        print(f"\n🔍 PROCESANDO CONSULTA FAISS")
        print(f"Query: {query}")
        print("-" * 50)
        
        # 1. Búsqueda FAISS + Árboles
        search_results = self.faiss_system.search(query, k=k, k_roots=k_roots)
        
        if not search_results:
            return "❌ No se encontraron resultados relevantes para tu consulta."
        
        # 2. Preparar contexto
        context = self._prepare_context(search_results, query)
        
        # 3. Generar respuesta
        prompt = self._build_prompt(query, context)
        
        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            print(f"❌ Error generando respuesta: {e}")
            return f"Error generando respuesta con LLM. Resultados encontrados: {len(search_results)} chunks relevantes."
    
    def _prepare_context(self, search_results: List, query: str) -> Dict[str, Any]:
        """Preparar contexto enriquecido para el LLM"""
        
        context = {
            'main_chunks': [],
            'document_sources': set(),
            'hierarchical_info': {},
            'cross_references': []
        }
        
        # Procesar resultados principales
        for chunk_id, score, doc_id in search_results:
            chunk_content = None
            
            # Obtener contenido del chunk
            for doc_name, hierarchical_graph in self.faiss_system.root_finder.document_trees.items():
                if hierarchical_graph.chunk_exists(chunk_id):
                    chunk_content = hierarchical_graph.get_chunk_content(chunk_id)
                    break
            
            if chunk_content:
                context['main_chunks'].append({
                    'id': chunk_id,
                    'content': chunk_content,
                    'score': score,
                    'document': doc_id
                })
                context['document_sources'].add(doc_id)
        
        # Obtener contexto adicional del primer resultado
        if search_results:
            first_chunk_id = search_results[0][0]
            
            # Contexto dentro del documento
            doc_context = self.faiss_system.get_document_context(first_chunk_id, context_size=2)
            
            # Contexto entre documentos
            cross_context = self.faiss_system.get_cross_document_context(first_chunk_id, query, max_docs=2)
            
            # Agregar contenido de contextos
            for chunk_id in doc_context + cross_context:
                for doc_name, hierarchical_graph in self.faiss_system.root_finder.document_trees.items():
                    if hierarchical_graph.chunk_exists(chunk_id):
                        content = hierarchical_graph.get_chunk_content(chunk_id)
                        if content:
                            context['cross_references'].append({
                                'id': chunk_id,
                                'content': content,
                                'document': doc_name
                            })
                        break
        
        return context
    
    def _build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """Construir prompt optimizado para el LLM"""
        
        prompt_parts = [
            "Eres un asistente experto que responde preguntas basándose en documentos técnicos.",
            f"CONSULTA: {query}",
            "",
            "INFORMACIÓN RELEVANTE:"
        ]
        
        # Agregar chunks principales
        for i, chunk in enumerate(context['main_chunks'], 1):
            prompt_parts.extend([
                f"[FRAGMENTO {i}] (Score: {chunk['score']:.3f}, Documento: {chunk['document']})",
                chunk['content'],
                ""
            ])
        
        # Agregar contexto adicional si existe
        if context['cross_references']:
            prompt_parts.append("CONTEXTO ADICIONAL:")
            for i, ref in enumerate(context['cross_references'][:3], 1):  # Limitar a 3
                prompt_parts.extend([
                    f"[CONTEXTO {i}] (Documento: {ref['document']})",
                    ref['content'][:300] + "..." if len(ref['content']) > 300 else ref['content'],
                    ""
                ])
        
        # Instrucciones finales
        prompt_parts.extend([
            "INSTRUCCIONES:",
            "1. Responde la consulta basándote únicamente en la información proporcionada",
            "2. Si la información no es suficiente, indícalo claramente",
            "3. Menciona las fuentes (documentos) cuando sea relevante",
            "4. Sé conciso pero completo",
            "",
            "RESPUESTA:"
        ])
        
        return "\\n".join(prompt_parts)
    
    def _test_search(self, query: str):
        """Realizar búsqueda de prueba sin LLM"""
        print(f"\n🧪 PRUEBA DE BÚSQUEDA: {query}")
        
        results = self.faiss_system.search(query, k=5, k_roots=5)
        
        if not results:
            print("❌ No se encontraron resultados")
            return
        
        print(f"\n📊 RESULTADOS ENCONTRADOS: {len(results)}")
        for i, (chunk_id, score, doc_id) in enumerate(results, 1):
            # Obtener contenido
            content = None
            for doc_name, hierarchical_graph in self.faiss_system.root_finder.document_trees.items():
                if hierarchical_graph.chunk_exists(chunk_id):
                    content = hierarchical_graph.get_chunk_content(chunk_id)
                    break
            
            preview = content[:100] + "..." if content and len(content) > 100 else content or "Sin contenido"
            print(f"   {i}. {chunk_id}")
            print(f"      📄 Documento: {doc_id}")
            print(f"      📊 Score: {score:.4f}")
            print(f"      📝 Preview: {preview}")
            print()
    
    def _show_stats(self):
        """Mostrar estadísticas del sistema"""
        self.faiss_system.print_system_summary()
    
    def _show_documents(self):
        """Mostrar lista de documentos disponibles"""
        stats = self.faiss_system.get_stats()
        
        print(f"\n📚 DOCUMENTOS DISPONIBLES ({len(stats['document_ids'])})")
        print("-" * 40)
        
        for i, doc_id in enumerate(stats['document_ids'], 1):
            root_chunk = self.faiss_system.root_finder.root_chunks.get(doc_id, 'unknown')
            
            # Obtener estadísticas del documento
            if doc_id in self.faiss_system.root_finder.document_trees:
                hierarchical_graph = self.faiss_system.root_finder.document_trees[doc_id]
                doc_stats = hierarchical_graph.get_hierarchical_stats()
                chunk_count = doc_stats.get('total_chunks', 0)
            else:
                chunk_count = 0
            
            print(f"   {i}. {doc_id}")
            print(f"      🌿 Raíz: {root_chunk}")
            print(f"      📊 Chunks: {chunk_count}")
            print()
    
    def _show_help(self):
        """Mostrar ayuda del sistema"""
        print("\n📖 AYUDA DEL SISTEMA FAISS RAG")
        print("=" * 40)
        print("COMANDOS DISPONIBLES:")
        print("  • Consulta normal: Escribe tu pregunta directamente")
        print("  • 'stats' - Ver estadísticas del sistema")
        print("  • 'docs' - Listar documentos disponibles")
        print("  • 'test [query]' - Probar búsqueda sin generar respuesta")
        print("  • 'exit' - Salir del sistema")
        print()
        print("CARACTERÍSTICAS:")
        print("  • Búsqueda optimizada con FAISS en raíces")
        print("  • Contexto jerárquico dentro de documentos")
        print("  • Referencias cruzadas entre documentos")
        print("  • Scores combinados (FAISS + PageRank)")
        print()


if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)