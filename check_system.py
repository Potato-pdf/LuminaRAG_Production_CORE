#!/usr/bin/env python3
"""
🔍 VERIFICACIÓN DEL SISTEMA LUMINA RAG
======================================

Script para verificar que todos los componentes del sistema estén funcionando correctamente:
- Conexiones a servicios (Milvus, Ollama)
- Configuración del entorno
- Arquitectura jerárquica
- Integridad de datos
"""

import os
import sys
import traceback
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def main():
    """Verificación completa del sistema"""
    
    print("🔍 VERIFICACIÓN DEL SISTEMA LUMINA RAG")
    print("="*50)
    
    checks = [
        ("📋 Configuración del entorno", check_environment),
        ("🗄️ Conexión a Milvus", check_milvus_connection),
        ("🦙 Conexión a Ollama", check_ollama_connection),
        ("📁 Estructura de archivos", check_file_structure),
        ("🌳 Arquitectura jerárquica", check_hierarchical_architecture),
        ("💾 Integridad de datos", check_data_integrity),
        ("🔧 Dependencias Python", check_python_dependencies)
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n{name}...")
        try:
            status, message = check_func()
            results.append((name, status, message))
            
            if status:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        except Exception as e:
            results.append((name, False, f"Error: {e}"))
            print(f"❌ Error: {e}")
    
    # Resumen final
    print_summary(results)

def check_environment() -> Tuple[bool, str]:
    """Verificar configuración del entorno"""
    
    required_vars = [
        'CHUNK_SIZE', 'CHUNK_OVERLAP', 'CHUNK_WINDOW_SIZE',
        'EMBEDDING_DIM', 'EMBEDDING_MODEL',
        'MILVUS_HOST', 'MILVUS_PORT', 'MILVUS_USER', 'MILVUS_PASSWORD',
        'OLLAMA_MODEL', 'OLLAMA_BASE_URL',
        'PDF_DIRECTORY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        return False, f"Variables faltantes: {', '.join(missing_vars)}"
    
    # Verificar archivo .env
    if not os.path.exists('.env'):
        return False, "Archivo .env no encontrado"
    
    return True, f"Todas las {len(required_vars)} variables configuradas correctamente"

def check_milvus_connection() -> Tuple[bool, str]:
    """Verificar conexión a Milvus"""
    
    try:
        from src.db_milvus.connection import connect_milvus
        from pymilvus import utility
        
        # Intentar conectar
        connect_milvus()
        
        # Verificar que la conexión funcione
        collections = utility.list_collections()
        
        return True, f"Conexión exitosa. Colecciones disponibles: {len(collections)}"
        
    except ImportError as e:
        return False, f"Error importando módulo Milvus: {e}"
    except Exception as e:
        return False, f"Error conectando a Milvus: {e}"

def check_ollama_connection() -> Tuple[bool, str]:
    """Verificar conexión a Ollama"""
    
    try:
        from src.model_ai.choice_model_llama import connect_ollama
        
        llm = connect_ollama()
        
        # Probar una consulta simple
        response = llm.invoke("Hola, ¿funciona correctamente?")
        
        if response and len(response) > 0:
            return True, f"Conexión exitosa. Modelo responde correctamente"
        else:
            return False, "Modelo no responde o respuesta vacía"
            
    except ImportError as e:
        return False, f"Error importando módulo Ollama: {e}"
    except Exception as e:
        return False, f"Error conectando a Ollama: {e}"

def check_file_structure() -> Tuple[bool, str]:
    """Verificar estructura de archivos"""
    
    required_files = [
        'index.py',
        'query.py',
        'utils.py',
        'migrate_graph.py',
        'requirements.txt',
        'src/config/settings.py',
        'src/document_graph/hierarchical_graph.py',
        'src/document_graph/simple_graph.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        return False, f"Archivos faltantes: {', '.join(missing_files)}"
    
    # Verificar directorio de PDFs
    pdf_dir = os.getenv('PDF_DIRECTORY', 'pdfs')
    if not os.path.exists(pdf_dir):
        return False, f"Directorio de PDFs no existe: {pdf_dir}"
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf') or f.endswith('.docx')]
    
    return True, f"Estructura correcta. {len(pdf_files)} documentos en {pdf_dir}"

def check_hierarchical_architecture() -> Tuple[bool, str]:
    """Verificar arquitectura jerárquica"""
    
    try:
        from src.document_graph.hierarchical_graph import HierarchicalDocumentGraph
        from src.config import STORAGE_CONFIG
        
        # Verificar si existe grafo jerárquico
        hierarchical_path = STORAGE_CONFIG["graph_path"].replace(".pkl", "_hierarchical.pkl")
        
        if not os.path.exists(hierarchical_path):
            return False, f"Grafo jerárquico no encontrado en {hierarchical_path}"
        
        # Cargar y verificar grafo
        import pickle
        with open(hierarchical_path, 'rb') as f:
            graph = pickle.load(f)
        
        if not hasattr(graph, 'is_hierarchical') or not graph.is_hierarchical:
            return False, "El grafo cargado no es jerárquico"
        
        stats = graph.get_hierarchical_stats()
        
        return True, f"Arquitectura jerárquica válida. {stats['documents_count']} documentos, {stats['total_chunks']} chunks"
        
    except ImportError as e:
        return False, f"Error importando arquitectura jerárquica: {e}"
    except Exception as e:
        return False, f"Error verificando arquitectura: {e}"

def check_data_integrity() -> Tuple[bool, str]:
    """Verificar integridad de datos"""
    
    try:
        from src.config import STORAGE_CONFIG
        
        issues = []
        
        # Verificar directorio de grafos
        graphs_dir = STORAGE_CONFIG["graphs_dir"]
        if not os.path.exists(graphs_dir):
            issues.append("Directorio de grafos no existe")
        
        # Verificar archivos de grafo
        graph_files = []
        if os.path.exists(graphs_dir):
            graph_files = [f for f in os.listdir(graphs_dir) if f.endswith('.pkl')]
        
        if not graph_files:
            issues.append("No se encontraron archivos de grafo")
        
        # Verificar que los archivos sean válidos
        for graph_file in graph_files:
            try:
                import pickle
                with open(os.path.join(graphs_dir, graph_file), 'rb') as f:
                    graph = pickle.load(f)
                # Verificar que el grafo tenga métodos básicos
                if not hasattr(graph, 'get_stats'):
                    issues.append(f"Grafo inválido: {graph_file}")
            except Exception:
                issues.append(f"Error leyendo grafo: {graph_file}")
        
        if issues:
            return False, f"Problemas encontrados: {'; '.join(issues)}"
        
        return True, f"Integridad verificada. {len(graph_files)} archivos de grafo válidos"
        
    except Exception as e:
        return False, f"Error verificando integridad: {e}"

def check_python_dependencies() -> Tuple[bool, str]:
    """Verificar dependencias de Python"""
    
    required_packages = [
        'pymilvus',
        'ollama', 
        'llama_index',
        'sentence_transformers',
        'networkx',
        'dotenv',  # Cambiado de 'python-dotenv' a 'dotenv'
        'numpy',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        return False, f"Paquetes faltantes: {', '.join(missing_packages)}"
    
    return True, f"Todas las {len(required_packages)} dependencias disponibles"

def print_summary(results: List[Tuple[str, bool, str]]):
    """Imprimir resumen de verificaciones"""
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*50)
    
    passed = sum(1 for _, status, _ in results if status)
    total = len(results)
    
    print(f"\n✅ Verificaciones exitosas: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡Sistema completamente funcional!")
        print("\n🚀 COMANDOS DISPONIBLES:")
        print("   python3 index.py     # Indexar documentos")
        print("   python3 query.py     # Consultar sistema")
        print("   python3 utils.py     # Herramientas de gestión")
    else:
        print("⚠️ Algunos componentes requieren atención:")
        
        for name, status, message in results:
            if not status:
                print(f"   ❌ {name}: {message}")
        
        print("\n🔧 ACCIONES RECOMENDADAS:")
        print("   1. Verificar archivo .env con variables requeridas")
        print("   2. Iniciar servicios Docker (Milvus, Ollama)")
        print("   3. Instalar dependencias: pip install -r requirements.txt")
        print("   4. Ejecutar migración: python3 migrate_graph.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Verificación cancelada")
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        traceback.print_exc()
        sys.exit(1)