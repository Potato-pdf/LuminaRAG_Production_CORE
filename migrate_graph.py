#!/usr/bin/env python3
"""
🔄 MIGRADOR DE GRAFOS
====================

Migra grafos SimpleDocumentGraph existentes a HierarchicalDocumentGraph
Sin perder datos ni recomputar embeddings.
"""

import pickle
import os
from typing import Dict, List
from src.document_graph.simple_graph import SimpleDocumentGraph
from src.document_graph.hierarchical_graph import HierarchicalDocumentGraph
from src.config import STORAGE_CONFIG

def migrate_simple_to_hierarchical(
    simple_graph_path: str = None,
    output_path: str = None,
    preserve_original: bool = True
) -> HierarchicalDocumentGraph:
    """
    Migrar grafo simple existente a arquitectura jerárquica
    
    Args:
        simple_graph_path: Ruta al grafo simple (por defecto usa configuración)
        output_path: Ruta de salida (por defecto agrega '_hierarchical')
        preserve_original: Si mantener el archivo original
    
    Returns:
        HierarchicalDocumentGraph migrado
    """
    
    # Rutas por defecto
    if simple_graph_path is None:
        simple_graph_path = STORAGE_CONFIG["graph_path"]
    
    if output_path is None:
        output_path = simple_graph_path.replace(".pkl", "_hierarchical.pkl")
    
    print("🔄 MIGRACIÓN DE GRAFO")
    print("=" * 40)
    print(f"📥 Origen: {simple_graph_path}")
    print(f"📤 Destino: {output_path}")
    
    # 1. Cargar grafo simple existente
    print("📂 Cargando grafo simple...")
    try:
        with open(simple_graph_path, 'rb') as f:
            simple_graph = pickle.load(f)
        
        stats = simple_graph.get_stats()
        print(f"✅ Grafo simple cargado:")
        print(f"   📊 Nodos: {stats['nodes']}")
        print(f"   🔗 Conexiones: {stats['edges']}")
        
    except Exception as e:
        print(f"❌ Error cargando grafo simple: {e}")
        return None
    
    # 2. Extraer datos del grafo simple
    print("🔍 Extrayendo datos del grafo...")
    chunks_data = extract_chunks_from_simple_graph(simple_graph)
    print(f"✅ {len(chunks_data)} chunks extraídos")
    
    # 3. Crear nuevo grafo jerárquico
    print("🌳 Creando arquitectura jerárquica...")
    hierarchical_graph = HierarchicalDocumentGraph()
    hierarchical_graph.build_hierarchical(chunks_data)
    
    # 4. Preservar conexiones importantes del grafo original
    print("🔗 Preservando conexiones importantes...")
    preserve_important_connections(simple_graph, hierarchical_graph)
    
    # 5. Guardar grafo jerárquico
    print("💾 Guardando grafo jerárquico...")
    try:
        with open(output_path, 'wb') as f:
            pickle.dump(hierarchical_graph, f)
        print(f"✅ Grafo jerárquico guardado en: {output_path}")
        
    except Exception as e:
        print(f"❌ Error guardando grafo jerárquico: {e}")
        return None
    
    # 6. Crear backup del original si se requiere
    if preserve_original and not simple_graph_path.endswith("_backup.pkl"):
        backup_path = simple_graph_path.replace(".pkl", "_backup.pkl")
        try:
            import shutil
            shutil.copy2(simple_graph_path, backup_path)
            print(f"💾 Backup creado: {backup_path}")
        except Exception as e:
            print(f"⚠️ Warning: No se pudo crear backup: {e}")
    
    # 7. Mostrar comparación
    print("\n📊 COMPARACIÓN DE ARQUITECTURAS")
    print("=" * 40)
    
    simple_stats = simple_graph.get_stats()
    hierarchical_stats = hierarchical_graph.get_hierarchical_stats()
    
    print("📈 GRAFO SIMPLE (Original):")
    print(f"   Nodos: {simple_stats['nodes']}")
    print(f"   Conexiones: {simple_stats['edges']}")
    
    print("\n🌳 GRAFO JERÁRQUICO (Nuevo):")
    print(f"   Nodos: {hierarchical_stats['total_chunks']}")
    print(f"   Conexiones: {hierarchical_stats['total_connections']}")
    print(f"   Documentos: {hierarchical_stats['documents_count']}")
    print(f"   Raíces: {hierarchical_stats['document_roots']}")
    print(f"   Meta-conexiones: {hierarchical_stats['meta_graph_connections']}")
    
    hierarchical_graph.print_hierarchy_summary()
    
    print("\n🎉 ¡MIGRACIÓN COMPLETADA!")
    return hierarchical_graph

def extract_chunks_from_simple_graph(simple_graph: SimpleDocumentGraph) -> List[Dict]:
    """Extraer chunks y metadata del grafo simple"""
    chunks_data = []
    
    # Acceder al graph manager interno
    graph = simple_graph._manager.graph
    
    for node_id in graph.nodes():
        node_data = graph.nodes[node_id]
        
        # Extraer contenido y metadata
        content = node_data.get('content', '')
        metadata = node_data.get('metadata', {})
        
        # Asegurar que tenemos file_name para agrupación
        if 'file_name' not in metadata:
            metadata['file_name'] = 'migrated_document'
        
        chunk_data = {
            'id': node_id,
            'content': content,
            'metadata': metadata
        }
        chunks_data.append(chunk_data)
    
    return chunks_data

def preserve_important_connections(
    simple_graph: SimpleDocumentGraph, 
    hierarchical_graph: HierarchicalDocumentGraph
) -> None:
    """
    Preservar conexiones importantes del grafo original que no estén en la jerarquía
    """
    original_graph = simple_graph._manager.graph
    hierarchical_manager = hierarchical_graph._manager
    
    preserved_count = 0
    
    # Iterar sobre todas las conexiones originales
    for source, target, edge_data in original_graph.edges(data=True):
        weight = edge_data.get('weight', 1.0)
        
        # Verificar si ambos nodos existen en el grafo jerárquico
        if (hierarchical_manager.chunk_exists(source) and 
            hierarchical_manager.chunk_exists(target)):
            
            # Verificar si la conexión ya existe
            if not hierarchical_manager.graph.has_edge(source, target):
                # Preservar conexión importante
                hierarchical_manager.connect_chunks(source, target, weight)
                preserved_count += 1
    
    print(f"🔗 {preserved_count} conexiones adicionales preservadas")

def migrate_and_update_config(update_default: bool = False):
    """
    Función conveniente que migra y opcionalmente actualiza la configuración
    """
    hierarchical_graph = migrate_simple_to_hierarchical()
    
    if hierarchical_graph and update_default:
        # Actualizar configuración para usar grafo jerárquico por defecto
        hierarchical_path = STORAGE_CONFIG["graph_path"].replace(".pkl", "_hierarchical.pkl")
        
        print(f"🔧 Actualizando configuración para usar grafo jerárquico...")
        print(f"   Nuevo path por defecto: {hierarchical_path}")
        
        # Aquí podrías actualizar settings.py si fuera necesario
        # Por ahora solo informamos
    
    return hierarchical_graph

if __name__ == "__main__":
    import sys
    
    # Permitir argumentos de línea de comandos
    preserve_original = "--no-backup" not in sys.argv
    update_config = "--update-config" in sys.argv
    
    print("🔄 Iniciando migración de grafo...")
    result = migrate_and_update_config(update_default=update_config)
    
    if result:
        print("✅ Migración exitosa!")
        sys.exit(0)
    else:
        print("❌ Migración falló!")
        sys.exit(1)