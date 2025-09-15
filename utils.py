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
        print("1. 📊 Comparar grafos (simple vs jerárquico vs FAISS)")
        print("2. 🔄 Migrar sistema a FAISS")
        print("3. 🧹 Limpiar grafos obsoletos")
        print("4. 📈 Estadísticas detalladas")
        print("5. 🔍 Inspeccionar grafo específico")
        print("6. 🚀 Gestión sistema FAISS")
        print("7. 🧪 Probar sistema FAISS")
        print("8. 🚪 Salir")
        
        try:
            choice = input("\nSelecciona opción (1-8): ").strip()
            
            if choice == '1':
                compare_graphs()
            elif choice == '2':
                migrate_to_faiss_system()
            elif choice == '3':
                clean_obsolete_graphs()
            elif choice == '4':
                detailed_statistics()
            elif choice == '5':
                inspect_specific_graph()
            elif choice == '6':
                manage_faiss_system()
            elif choice == '7':
                test_faiss_system()
            elif choice == '8':
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
    """Comparar diferentes tipos de grafos incluyendo FAISS"""
    from src.config import STORAGE_CONFIG
    
    print("\n📊 COMPARACIÓN DE GRAFOS")
    print("="*40)
    
    graphs_dir = STORAGE_CONFIG["graphs_dir"]
    
    # Buscar archivos de grafos
    graph_files = []
    faiss_files = []
    
    if os.path.exists(graphs_dir):
        for file in os.listdir(graphs_dir):
            if file.endswith('.pkl'):
                if 'faiss' in file.lower():
                    faiss_files.append(os.path.join(graphs_dir, file))
                else:
                    graph_files.append(os.path.join(graphs_dir, file))
    
    total_files = len(graph_files) + len(faiss_files)
    if total_files == 0:
        print("❌ No se encontraron archivos de grafos")
        return
    
    print(f"📁 Encontrados {total_files} archivos:")
    
    # Mostrar grafos tradicionales
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
            else:
                print("   📝 Tipo: Simple")
                stats = graph.get_stats()
                print(f"   📊 Nodos: {stats['nodes']}")
                print(f"   🔗 Conexiones: {stats['edges']}")
                
        except Exception as e:
            print(f"   ❌ Error leyendo grafo: {e}")
    
    # Mostrar sistemas FAISS
    for i, faiss_file in enumerate(faiss_files, len(graph_files) + 1):
        print(f"\n{i}. {os.path.basename(faiss_file)}")
        
        try:
            with open(faiss_file, 'rb') as f:
                faiss_system = pickle.load(f)
            
            print("   � Tipo: Sistema FAISS")
            
            if hasattr(faiss_system, 'get_stats'):
                stats = faiss_system.get_stats()
                print(f"   � Documentos: {stats.get('total_documents', 0)}")
                print(f"   🌿 Raíces indexadas: {stats.get('indexed_roots', 0)}")
                print(f"   � Total chunks: {stats.get('total_chunks', 0)}")
                print(f"   🤖 Dimensión embeddings: {stats.get('embedding_dimension', 0)}")
                print(f"   ⚡ Estado: {'✅ Listo' if stats.get('is_built', False) else '⚠️ Requiere rebuild'}")
            else:
                print("   ⚠️ Sistema FAISS sin estadísticas")
                
        except Exception as e:
            print(f"   ❌ Error leyendo sistema FAISS: {e}")

def migrate_to_faiss_system():
    """Migrar sistema actual a FAISS-GPU"""
    print("\n🔄 MIGRACIÓN A SISTEMA FAISS-GPU")
    print("="*40)
    
    # Verificar si ya existe sistema FAISS
    from src.config import STORAGE_CONFIG
    graphs_dir = STORAGE_CONFIG["graphs_dir"]
    faiss_path = os.path.join(graphs_dir, "faiss_system.pkl")
    
    if os.path.exists(faiss_path):
        response = input(f"⚠️ Ya existe sistema FAISS. ¿Sobreescribir? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Migración cancelada")
            return
    
    try:
        from src.FAISS.faiss_integration import migrate_hierarchical_to_faiss
        
        print("\n🚀 Iniciando migración a FAISS...")
        success = migrate_hierarchical_to_faiss()
        
        if success:
            print("\n✅ ¡Migración a FAISS-GPU completada!")
            print("💡 Ahora puedes usar: python3 query_faiss.py")
        else:
            print("❌ Migración a FAISS-GPU fallida")
            
    except Exception as e:
        print(f"❌ Error en migración: {e}")

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
    """Mostrar estadísticas detalladas incluyendo FAISS"""
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
                print(f"   📈 Conectividad cruzada: {stats.get('cross_document_connectivity', 0):.2%}")
                print(f"   📊 Promedio chunks/documento: {stats.get('avg_chunks_per_document', 0):.1f}")
                
                if 'document_tree_depths' in stats:
                    print(f"\n   🌳 Profundidades por documento:")
                    for doc, depth in stats['document_tree_depths'].items():
                        print(f"      📄 {doc}: {depth} niveles")
                
        except Exception as e:
            print(f"   ❌ Error leyendo grafo jerárquico: {e}")
    else:
        print("⚠️ No se encontró grafo jerárquico")
    
    # Cargar sistema FAISS si existe
    faiss_path = os.path.join(STORAGE_CONFIG["graphs_dir"], "faiss_system.pkl")
    
    if os.path.exists(faiss_path):
        print(f"\n🚀 SISTEMA FAISS:")
        try:
            from src.FAISS.faiss_integration import load_faiss_system
            
            faiss_system = load_faiss_system()
            if faiss_system:
                stats = faiss_system.get_stats()
                
                print(f"   📄 Documentos indexados: {stats.get('total_documents', 0)}")
                print(f"   � Raíces en FAISS: {stats.get('indexed_roots', 0)}")
                print(f"   📊 Total chunks: {stats.get('total_chunks', 0)}")
                print(f"   🔗 Total conexiones: {stats.get('total_connections', 0)}")
                print(f"   📏 Profundidad promedio: {stats.get('average_tree_depth', 0):.1f}")
                print(f"   🤖 Dimensión embeddings: {stats.get('embedding_dimension', 0)}")
                print(f"   ⚡ Estado: {('✅ Listo' if stats.get('is_built', False) else '⚠️ Requiere rebuild')}")
                
                if stats.get('document_ids'):
                    print(f"\n   📚 Documentos disponibles:")
                    for doc_id in stats['document_ids'][:5]:  # Mostrar solo 5
                        print(f"      📄 {doc_id}")
                    if len(stats['document_ids']) > 5:
                        print(f"      ... y {len(stats['document_ids']) - 5} más")
            else:
                print("   ❌ Error cargando sistema FAISS")
                
        except Exception as e:
            print(f"   ❌ Error con sistema FAISS: {e}")
    else:
        print("⚠️ No se encontró sistema FAISS")
        print("💡 Ejecutar: python3 migrate_to_faiss.py")
    
    # Información del sistema
    print(f"\n💾 INFORMACIÓN DE ALMACENAMIENTO:")
    graphs_dir = STORAGE_CONFIG["graphs_dir"]
    if os.path.exists(graphs_dir):
        total_size = 0
        file_count = 0
        faiss_count = 0
        
        for file in os.listdir(graphs_dir):
            if file.endswith('.pkl'):
                file_path = os.path.join(graphs_dir, file)
                size = os.path.getsize(file_path)
                total_size += size
                file_count += 1
                
                if 'faiss' in file.lower():
                    faiss_count += 1
                    print(f"   🚀 {file}: {size/1024:.1f} KB (FAISS)")
                else:
                    print(f"   📁 {file}: {size/1024:.1f} KB")
        
        print(f"\n   📊 Resumen: {file_count} archivos ({faiss_count} FAISS), {total_size/1024:.1f} KB total")
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


def manage_faiss_system():
    """Gestión del sistema FAISS"""
    print("\n🚀 GESTIÓN SISTEMA FAISS")
    print("="*40)
    
    while True:
        print("\n📋 OPCIONES FAISS:")
        print("1. 📊 Estado del sistema FAISS")
        print("2. 🔄 Reconstruir índice FAISS")
        print("3. 💾 Crear backup del sistema")
        print("4. 📂 Cargar sistema FAISS")
        print("5. 🗑️ Eliminar sistema FAISS")
        print("6. ↩️ Volver al menú principal")
        
        try:
            choice = input("\nSelecciona opción (1-6): ").strip()
            
            if choice == '1':
                show_faiss_status()
            elif choice == '2':
                rebuild_faiss_index()
            elif choice == '3':
                backup_faiss_system()
            elif choice == '4':
                load_faiss_system_info()
            elif choice == '5':
                delete_faiss_system()
            elif choice == '6':
                break
            else:
                print("❌ Opción inválida")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def show_faiss_status():
    """Mostrar estado del sistema FAISS"""
    try:
        from src.FAISS.faiss_integration import load_faiss_system
        
        faiss_system = load_faiss_system()
        if faiss_system:
            print("\n✅ SISTEMA FAISS CARGADO")
            faiss_system.print_system_summary()
        else:
            print("❌ Sistema FAISS no encontrado")
            print("💡 Ejecutar: python3 migrate_to_faiss.py")
            
    except Exception as e:
        print(f"❌ Error verificando sistema FAISS: {e}")


def rebuild_faiss_index():
    """Reconstruir índice FAISS"""
    try:
        from src.FAISS.faiss_integration import load_faiss_system
        
        print("\n🔄 RECONSTRUYENDO ÍNDICE FAISS...")
        
        faiss_system = load_faiss_system()
        if not faiss_system:
            print("❌ Sistema FAISS no encontrado")
            return
        
        # Reconstruir índice
        success = faiss_system.build_index()
        
        if success:
            print("✅ Índice FAISS reconstruido exitosamente")
            
            # Guardar sistema actualizado
            from src.FAISS.faiss_integration import save_faiss_system
            save_faiss_system(faiss_system)
        else:
            print("❌ Error reconstruyendo índice FAISS")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def backup_faiss_system():
    """Crear backup del sistema FAISS"""
    try:
        from src.config import STORAGE_CONFIG
        import shutil
        from datetime import datetime
        
        graphs_dir = STORAGE_CONFIG["graphs_dir"]
        faiss_path = os.path.join(graphs_dir, "faiss_system.pkl")
        
        if not os.path.exists(faiss_path):
            print("❌ Sistema FAISS no encontrado")
            return
        
        # Crear nombre de backup con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"faiss_system_backup_{timestamp}.pkl"
        backup_path = os.path.join(graphs_dir, backup_name)
        
        # Copiar archivo
        shutil.copy2(faiss_path, backup_path)
        print(f"💾 Backup creado: {backup_name}")
        
    except Exception as e:
        print(f"❌ Error creando backup: {e}")


def load_faiss_system_info():
    """Cargar información del sistema FAISS"""
    try:
        from src.FAISS.faiss_integration import load_faiss_system, verify_faiss_system
        
        print("\n📂 CARGANDO SISTEMA FAISS...")
        
        faiss_system = load_faiss_system()
        if faiss_system:
            print("✅ Sistema FAISS cargado exitosamente")
            
            # Verificar funcionamiento
            if verify_faiss_system(faiss_system):
                print("✅ Sistema FAISS verificado y funcionando")
            else:
                print("⚠️ Sistema FAISS cargado pero con problemas")
        else:
            print("❌ No se pudo cargar sistema FAISS")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def delete_faiss_system():
    """Eliminar sistema FAISS"""
    from src.config import STORAGE_CONFIG
    
    graphs_dir = STORAGE_CONFIG["graphs_dir"]
    faiss_path = os.path.join(graphs_dir, "faiss_system.pkl")
    
    if not os.path.exists(faiss_path):
        print("❌ Sistema FAISS no encontrado")
        return
    
    response = input("⚠️ ¿Estás seguro de eliminar el sistema FAISS? (y/N): ").strip().lower()
    
    if response == 'y':
        try:
            os.remove(faiss_path)
            print("🗑️ Sistema FAISS eliminado")
            print("💡 Para recrear: python3 migrate_to_faiss.py")
        except Exception as e:
            print(f"❌ Error eliminando: {e}")
    else:
        print("❌ Eliminación cancelada")


def test_faiss_system():
    """Probar sistema FAISS con consultas de ejemplo"""
    print("\n🧪 PRUEBA DEL SISTEMA FAISS")
    print("="*40)
    
    try:
        from src.FAISS.faiss_integration import load_faiss_system
        
        faiss_system = load_faiss_system()
        if not faiss_system:
            print("❌ Sistema FAISS no disponible")
            return
        
        # Consultas de prueba
        test_queries = [
            "¿Cuáles son los procedimientos principales?",
            "¿Qué información contienen los documentos?",
            "¿Cómo funciona el proceso de cobranza?",
            "¿Qué normativas se mencionan?"
        ]
        
        print("🔍 Ejecutando consultas de prueba...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            print("-" * 50)
            
            results = faiss_system.search(query, k=3, k_roots=3)
            
            if results:
                print(f"✅ {len(results)} resultados encontrados:")
                for j, (chunk_id, score, doc_id) in enumerate(results, 1):
                    print(f"   {j}. {chunk_id[:20]}... (doc: {doc_id}) - Score: {score:.4f}")
            else:
                print("❌ Sin resultados")
            
            if i < len(test_queries):
                input("\nPresiona Enter para continuar...")
        
        print("\n✅ Pruebas completadas")
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
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