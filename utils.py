#!/usr/bin/env python3
"""
🔧 UTILIDADES DE GESTIÓN DE GRAFOS
=================================

Herramientas para gestionar diferentes tipos de grafos:
- Migración de grafos simples a jerárquicos
- Comparación de arquitecturas
- Limpieza y mantenimiento
- Estadísticas detalladas
"""

import os
import pickle
import sys
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def main():
    """Menú principal de utilidades"""
    
    print("🔧 UTILIDADES DE GRAFOS LUMINA")
    print("="*40)
    
    while True:
        print("\n📋 OPCIONES DISPONIBLES:")
        print("1. 📊 Comparar grafos (simple vs jerárquico)")
        print("2. 🔄 Migrar grafo simple a jerárquico")
        print("3. 🧹 Limpiar grafos obsoletos")
        print("4. 📈 Estadísticas detalladas")
        print("5. 🔍 Inspeccionar grafo específico")
        print("6. 🚪 Salir")
        
        try:
            choice = input("\nSelecciona opción (1-6): ").strip()
            
            if choice == '1':
                compare_graphs()
            elif choice == '2':
                migrate_simple_to_hierarchical()
            elif choice == '3':
                clean_obsolete_graphs()
            elif choice == '4':
                detailed_statistics()
            elif choice == '5':
                inspect_specific_graph()
            elif choice == '6':
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def compare_graphs():
    """Comparar diferentes tipos de grafos"""
    from src.config import STORAGE_CONFIG
    
    print("\n📊 COMPARACIÓN DE GRAFOS")
    print("="*40)
    
    graphs_dir = STORAGE_CONFIG["graphs_dir"]
    
    # Buscar archivos de grafos
    graph_files = []
    if os.path.exists(graphs_dir):
        for file in os.listdir(graphs_dir):
            if file.endswith('.pkl'):
                graph_files.append(os.path.join(graphs_dir, file))
    
    if not graph_files:
        print("❌ No se encontraron archivos de grafos")
        return
    
    print(f"📁 Encontrados {len(graph_files)} archivos de grafos:")
    
    for i, graph_file in enumerate(graph_files, 1):
        print(f"\n{i}. {os.path.basename(graph_file)}")
        
        try:
            with open(graph_file, 'rb') as f:
                graph = pickle.load(f)
            
            # Determinar tipo de grafo
            if hasattr(graph, 'is_hierarchical') and graph.is_hierarchical:
                print("   🌳 Tipo: Jerárquico")
                stats = graph.get_hierarchical_stats()
                print(f"   📄 Documentos: {stats['documents_count']}")
                print(f"   🌿 Raíces: {stats['document_roots']}")
                print(f"   📊 Chunks: {stats['total_chunks']}")
                print(f"   🔗 Conexiones: {stats['total_connections']}")
                print(f"   🌐 Meta-conexiones: {stats['meta_graph_connections']}")
            else:
                print("   📝 Tipo: Simple")
                stats = graph.get_stats()
                print(f"   📊 Nodos: {stats['nodes']}")
                print(f"   🔗 Conexiones: {stats['edges']}")
                
        except Exception as e:
            print(f"   ❌ Error leyendo grafo: {e}")

def migrate_simple_to_hierarchical():
    """Migración eliminada - usar directamente indexación jerárquica"""
    print("⚠️ Migración eliminada: usar 'python3 index.py' directamente")
    return False

def clean_obsolete_graphs():
    """Limpiar grafos obsoletos"""
    from src.config import STORAGE_CONFIG
    
    print("\n🧹 LIMPIEZA DE GRAFOS OBSOLETOS")
    print("="*40)
    
    graphs_dir = STORAGE_CONFIG["graphs_dir"]
    
    if not os.path.exists(graphs_dir):
        print("❌ Directorio de grafos no existe")
        return
    
    # Encontrar archivos potencialmente obsoletos
    obsolete_patterns = ['_backup.pkl', '_legacy.pkl', '_old.pkl']
    obsolete_files = []
    
    for file in os.listdir(graphs_dir):
        if any(pattern in file for pattern in obsolete_patterns):
            obsolete_files.append(os.path.join(graphs_dir, file))
    
    if not obsolete_files:
        print("✅ No se encontraron archivos obsoletos")
        return
    
    print(f"📁 Archivos potencialmente obsoletos:")
    for file in obsolete_files:
        print(f"   • {os.path.basename(file)}")
    
    response = input(f"\n⚠️ ¿Eliminar {len(obsolete_files)} archivos? (y/N): ").strip().lower()
    
    if response == 'y':
        for file in obsolete_files:
            try:
                os.remove(file)
                print(f"🗑️ Eliminado: {os.path.basename(file)}")
            except Exception as e:
                print(f"❌ Error eliminando {file}: {e}")
        print("✅ Limpieza completada")
    else:
        print("❌ Limpieza cancelada")

def detailed_statistics():
    """Mostrar estadísticas detalladas"""
    from src.config import STORAGE_CONFIG
    
    print("\n📈 ESTADÍSTICAS DETALLADAS")
    print("="*40)
    
    # Cargar grafo jerárquico si existe
    hierarchical_path = STORAGE_CONFIG["graph_path"].replace(".pkl", "_hierarchical.pkl")
    
    if os.path.exists(hierarchical_path):
        print("🌳 GRAFO JERÁRQUICO:")
        try:
            with open(hierarchical_path, 'rb') as f:
                graph = pickle.load(f)
            
            if hasattr(graph, 'is_hierarchical') and graph.is_hierarchical:
                stats = graph.get_hierarchical_stats()
                
                print(f"   📄 Documentos: {stats['documents_count']}")
                print(f"   🌿 Raíces: {stats['document_roots']}")
                print(f"   📊 Total chunks: {stats['total_chunks']}")
                print(f"   🔗 Total conexiones: {stats['total_connections']}")
                print(f"   🌐 Meta-conexiones: {stats['meta_graph_connections']}")
                print(f"   📈 Conectividad cruzada: {stats.get('cross_document_connectivity', 0):.2%}")
                print(f"   📊 Promedio chunks/documento: {stats.get('avg_chunks_per_document', 0):.1f}")
                
                if 'document_tree_depths' in stats:
                    print(f"\n   🌳 Profundidades por documento:")
                    for doc, depth in stats['document_tree_depths'].items():
                        print(f"      📄 {doc}: {depth} niveles")
                
                # Mostrar resumen de arquitectura
                print(f"\n   🏗️ RESUMEN DE ARQUITECTURA:")
                graph.print_hierarchy_summary()
                
        except Exception as e:
            print(f"   ❌ Error leyendo grafo jerárquico: {e}")
    else:
        print("⚠️ No se encontró grafo jerárquico")
    
    # Información del sistema
    print(f"\n💾 INFORMACIÓN DE ALMACENAMIENTO:")
    graphs_dir = STORAGE_CONFIG["graphs_dir"]
    if os.path.exists(graphs_dir):
        total_size = 0
        file_count = 0
        for file in os.listdir(graphs_dir):
            if file.endswith('.pkl'):
                file_path = os.path.join(graphs_dir, file)
                size = os.path.getsize(file_path)
                total_size += size
                file_count += 1
                print(f"   📁 {file}: {size/1024:.1f} KB")
        
        print(f"   📊 Total: {file_count} archivos, {total_size/1024:.1f} KB")
    else:
        print("   ❌ Directorio de grafos no existe")

def inspect_specific_graph():
    """Inspeccionar un grafo específico"""
    from src.config import STORAGE_CONFIG
    
    print("\n🔍 INSPECCIÓN DE GRAFO ESPECÍFICO")
    print("="*40)
    
    graphs_dir = STORAGE_CONFIG["graphs_dir"]
    
    if not os.path.exists(graphs_dir):
        print("❌ Directorio de grafos no existe")
        return
    
    # Listar archivos disponibles
    graph_files = [f for f in os.listdir(graphs_dir) if f.endswith('.pkl')]
    
    if not graph_files:
        print("❌ No se encontraron archivos de grafos")
        return
    
    print("📁 Archivos disponibles:")
    for i, file in enumerate(graph_files, 1):
        print(f"{i}. {file}")
    
    try:
        choice = int(input(f"\nSelecciona archivo (1-{len(graph_files)}): "))
        if 1 <= choice <= len(graph_files):
            selected_file = graph_files[choice - 1]
            inspect_graph_file(os.path.join(graphs_dir, selected_file))
        else:
            print("❌ Selección inválida")
    except ValueError:
        print("❌ Entrada inválida")

def inspect_graph_file(file_path: str):
    """Inspeccionar archivo de grafo específico"""
    print(f"\n🔍 Inspeccionando: {os.path.basename(file_path)}")
    print("="*40)
    
    try:
        with open(file_path, 'rb') as f:
            graph = pickle.load(f)
        
        # Información básica
        print(f"📁 Archivo: {file_path}")
        print(f"💾 Tamaño: {os.path.getsize(file_path)/1024:.1f} KB")
        
        # Tipo de grafo y estadísticas
        if hasattr(graph, 'is_hierarchical') and graph.is_hierarchical:
            print("🌳 Tipo: Grafo Jerárquico")
            stats = graph.get_hierarchical_stats()
            
            print(f"\n📊 ESTADÍSTICAS:")
            for key, value in stats.items():
                if isinstance(value, dict):
                    print(f"   {key}:")
                    for subkey, subvalue in value.items():
                        print(f"      {subkey}: {subvalue}")
                else:
                    print(f"   {key}: {value}")
            
            # Mostrar algunos chunks de ejemplo
            print(f"\n📄 MUESTRA DE CHUNKS:")
            important_chunks = graph.get_most_important_chunks_hierarchical(top_k=3)
            for i, (chunk_id, score, doc_name) in enumerate(important_chunks, 1):
                content = graph.get_chunk_content(chunk_id)
                print(f"   {i}. [{doc_name}] Score: {score:.3f}")
                print(f"      ID: {chunk_id}")
                print(f"      Contenido: {content[:100] if content else 'N/A'}...")
                
        else:
            print("📝 Tipo: Grafo Simple")
            stats = graph.get_stats()
            
            print(f"\n📊 ESTADÍSTICAS:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
            
            # Mostrar algunos chunks importantes
            print(f"\n📄 MUESTRA DE CHUNKS:")
            important_chunks = graph.get_most_important_chunks(top_k=3)
            for i, (chunk_id, score) in enumerate(important_chunks, 1):
                content = graph.get_chunk_content(chunk_id)
                print(f"   {i}. Score: {score:.3f}")
                print(f"      ID: {chunk_id}")
                print(f"      Contenido: {content[:100] if content else 'N/A'}...")
        
    except Exception as e:
        print(f"❌ Error inspeccionando grafo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error en utilidades: {e}")
        sys.exit(1)