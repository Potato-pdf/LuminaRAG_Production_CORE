#!/usr/bin/env python3
"""
🔄 MIGRACIÓN A SISTEMA FAISS
============================

Script para migrar desde el sistema de grafo jerárquico actual
al nuevo sistema optimizado con FAISS + árboles independientes.

Proceso:
1. Cargar grafo jerárquico existente
2. Extraer documentos y raíces
3. Crear sistema FAISS
4. Guardar nuevo sistema
5. Verificar funcionamiento
"""

import os
import sys
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

def main():
    """Proceso principal de migración"""
    
    print("🔄 MIGRACIÓN: JERÁRQUICO → FAISS-GPU")
    print("=" * 50)
    
    # 1. Verificar sistema actual
    print("🔍 Verificando sistema actual...")
    if not verify_current_system():
        return False
    
    # 2. Realizar migración
    print("\\n🚀 Iniciando migración...")
    success = perform_migration()
    
    if not success:
        print("❌ Migración fallida")
        return False
    
    # 3. Verificar nuevo sistema
    print("\\n✅ Verificando nuevo sistema FAISS...")
    if verify_faiss_system():
        print("\\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print_migration_summary()
        return True
    else:
        print("❌ Verificación del sistema FAISS fallida")
        return False


def verify_current_system() -> bool:
    """Verificar que el sistema jerárquico actual esté disponible"""
    
    try:
        from src.config import STORAGE_CONFIG
        
        # Verificar archivo de grafo jerárquico
        graphs_dir = STORAGE_CONFIG["graphs_dir"]
        hierarchical_path = os.path.join(graphs_dir, "document_graph_hierarchical.pkl")
        
        if not os.path.exists(hierarchical_path):
            print(f"❌ Grafo jerárquico no encontrado: {hierarchical_path}")
            print("💡 Ejecutar primero: python3 index.py")
            return False
        
        # Verificar que se pueda cargar
        import pickle
        with open(hierarchical_path, 'rb') as f:
            hierarchical_graph = pickle.load(f)
        
        if not hasattr(hierarchical_graph, 'is_hierarchical') or not hierarchical_graph.is_hierarchical:
            print("❌ El grafo cargado no es jerárquico")
            return False
        
        # Mostrar estadísticas actuales
        stats = hierarchical_graph.get_hierarchical_stats()
        print(f"✅ Sistema jerárquico encontrado:")
        print(f"   📄 Documentos: {stats.get('documents_count', 0)}")
        print(f"   📊 Total chunks: {stats.get('total_chunks', 0)}")
        print(f"   🌿 Raíces: {stats.get('document_roots', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando sistema actual: {e}")
        return False


def perform_migration() -> bool:
    """Realizar la migración completa"""
    
    try:
        from src.FAISS.faiss_integration import migrate_hierarchical_to_faiss
        
        # Ejecutar migración
        success = migrate_hierarchical_to_faiss()
        
        if success:
            print("✅ Migración de datos completada")
            return True
        else:
            print("❌ Error en migración de datos")
            return False
            
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_faiss_system() -> bool:
    """Verificar que el nuevo sistema FAISS funcione"""
    
    try:
        from src.FAISS.faiss_integration import load_faiss_system, verify_faiss_system
        
        # Cargar sistema FAISS
        faiss_system = load_faiss_system()
        if not faiss_system:
            print("❌ No se pudo cargar sistema FAISS")
            return False
        
        # Verificar funcionamiento
        return verify_faiss_system(faiss_system)
        
    except Exception as e:
        print(f"❌ Error verificando sistema FAISS: {e}")
        return False


def test_faiss_search():
    """Probar búsqueda FAISS con consulta de ejemplo"""
    
    try:
        from src.FAISS.faiss_integration import load_faiss_system
        
        # Cargar sistema
        faiss_system = load_faiss_system()
        if not faiss_system:
            return False
        
        # Consulta de prueba
        test_query = "¿Cuáles son los procedimientos principales?"
        print(f"\\n🧪 PRUEBA DE BÚSQUEDA FAISS")
        print(f"Query: {test_query}")
        print("-" * 40)
        
        results = faiss_system.search(test_query, k=3, k_roots=3)
        
        if results:
            print(f"✅ Búsqueda exitosa: {len(results)} resultados")
            for i, (chunk_id, score, doc_id) in enumerate(results, 1):
                print(f"   {i}. {chunk_id} (doc: {doc_id}, score: {score:.4f})")
            return True
        else:
            print("⚠️ Búsqueda sin resultados")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de búsqueda: {e}")
        return False


def print_migration_summary():
    """Imprimir resumen de la migración"""
    
    print("\\n" + "=" * 60)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("=" * 60)
    
    print("🔄 CAMBIOS REALIZADOS:")
    print("   ❌ Meta-grafo eliminado completamente")
    print("   ✅ Sistema FAISS para búsqueda por raíces")
    print("   ✅ Árboles jerárquicos independientes por documento")
    print("   ✅ Scores combinados (FAISS + PageRank)")
    
    print("\\n🚀 ARCHIVOS DISPONIBLES:")
    print("   📝 query_faiss.py - Sistema de consultas optimizado")
    print("   🔧 src/FAISS/ - Módulos FAISS completos")
    print("   📊 Sistema guardado en graphs/faiss_system.pkl")
    
    print("\\n💡 COMANDOS DISPONIBLES:")
    print("   python3 query_faiss.py    # Consultas interactivas")
    print("   python3 check_system.py   # Verificación general")
    
    print("\\n⚡ VENTAJAS DEL NUEVO SISTEMA:")
    print("   🔍 Búsqueda ultra-rápida con FAISS")
    print("   🎯 Solo busca en documentos relevantes")
    print("   🌳 Mantiene estructura jerárquica por documento")
    print("   📈 Mejor precisión con scores combinados")
    print("   🧹 Arquitectura más limpia y mantenible")
    
    print("=" * 60)


def interactive_migration():
    """Migración interactiva con confirmaciones"""
    
    print("🔄 MIGRACIÓN INTERACTIVA")
    print("-" * 30)
    
    # Confirmación del usuario
    response = input("¿Continuar con la migración? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Migración cancelada")
        return False
    
    # Verificar si ya existe sistema FAISS
    from src.config import STORAGE_CONFIG
    graphs_dir = STORAGE_CONFIG["graphs_dir"]
    faiss_path = os.path.join(graphs_dir, "faiss_system.pkl")
    
    if os.path.exists(faiss_path):
        print(f"⚠️ Ya existe sistema FAISS: {faiss_path}")
        response = input("¿Sobreescribir? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Migración cancelada")
            return False
    
    # Realizar migración
    return main()


if __name__ == "__main__":
    try:
        # Verificar argumentos
        if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
            success = interactive_migration()
        else:
            success = main()
        
        if success:
            # Opcional: probar búsqueda
            if len(sys.argv) > 1 and sys.argv[1] == "--test":
                test_faiss_search()
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\\n👋 Migración cancelada")
    except Exception as e:
        print(f"❌ Error crítico en migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)