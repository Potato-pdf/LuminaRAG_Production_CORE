"""
🔗 INTEGRACIÓN FAISS CON SISTEMA RAG
====================================

Integra el sistema FAISS con el pipeline existente de indexación y consultas.
Reemplaza el meta-grafo con búsqueda eficiente por raíces.
"""

import os
import pickle
from typing import List, Dict, Optional
from .tree_graph import TreeGraphRAG
from ..config import STORAGE_CONFIG


def create_faiss_system_from_hierarchical(hierarchical_graph) -> TreeGraphRAG:
    """
    Crear sistema FAISS desde un grafo jerárquico existente
    
    Args:
        hierarchical_graph: Grafo jerárquico con documentos indexados
        
    Returns:
        TreeGraphRAG configurado y listo
    """
    print("\n🔄 CREANDO SISTEMA FAISS DESDE GRAFO JERÁRQUICO")
    print("=" * 50)
    
    # 1. Inicializar sistema FAISS
    faiss_system = TreeGraphRAG()
    
    # 2. Obtener raíces de documentos
    document_roots = hierarchical_graph.get_document_roots()
    documents_list = hierarchical_graph.get_documents_list()
    
    print(f"📄 Documentos encontrados: {len(documents_list)}")
    
    # 3. Agregar cada documento al sistema FAISS
    for doc_name in documents_list:
        if doc_name in document_roots:
            root_chunk_id = document_roots[doc_name]
            
            # Crear un subgrafo para este documento específico
            doc_chunks = hierarchical_graph.get_chunks_by_document(doc_name)
            doc_hierarchical_graph = extract_document_subgraph(hierarchical_graph, doc_name, doc_chunks)
            
            # Agregar al sistema FAISS
            faiss_system.add_document(doc_name, doc_hierarchical_graph, root_chunk_id)
            print(f"   ✅ {doc_name}: {len(doc_chunks)} chunks, raíz: {root_chunk_id}")
        else:
            print(f"   ⚠️ {doc_name}: No se encontró raíz")
    
    # 4. Construir índice FAISS
    print("\n🏗️ Construyendo índice FAISS...")
    success = faiss_system.build_index()
    
    if success:
        print("✅ Sistema FAISS creado exitosamente")
        faiss_system.print_system_summary()
    else:
        print("❌ Error creando sistema FAISS")
        
    return faiss_system


def extract_document_subgraph(hierarchical_graph, doc_name: str, doc_chunks: List[str]):
    """
    Extraer un subgrafo para un documento específico
    
    Args:
        hierarchical_graph: Grafo jerárquico completo
        doc_name: Nombre del documento
        doc_chunks: Lista de chunks del documento
        
    Returns:
        Subgrafo jerárquico solo para este documento
    """
    from ..document_graph.hierarchical_graph import HierarchicalDocumentGraph
    
    # Crear nuevo grafo jerárquico para este documento
    doc_graph = HierarchicalDocumentGraph()
    
    # Copiar chunks del documento
    for chunk_id in doc_chunks:
        content = hierarchical_graph.get_chunk_content(chunk_id)
        metadata = hierarchical_graph._manager.get_chunk_metadata(chunk_id)
        if content:
            doc_graph.add_chunk(chunk_id, content, metadata)
    
    # Copiar conexiones del documento
    for chunk_id in doc_chunks:
        # Obtener vecinos en el grafo original
        if hierarchical_graph._manager.graph.has_node(chunk_id):
            neighbors = list(hierarchical_graph._manager.graph.neighbors(chunk_id))
            for neighbor in neighbors:
                if neighbor in doc_chunks:  # Solo conexiones dentro del documento
                    # Obtener peso de la conexión
                    edge_data = hierarchical_graph._manager.graph.get_edge_data(chunk_id, neighbor)
                    weight = edge_data.get('weight', 1.0) if edge_data else 1.0
                    doc_graph.connect_chunks(chunk_id, neighbor, weight)
    
    # Marcar como jerárquico
    doc_graph._is_hierarchical = True
    doc_graph._document_roots = {doc_name: hierarchical_graph.get_document_roots()[doc_name]}
    doc_graph._document_graphs = {doc_name: doc_chunks}
    
    return doc_graph


def save_faiss_system(faiss_system: TreeGraphRAG, custom_path: str = None) -> bool:
    """
    Guardar sistema FAISS en disco
    
    Args:
        faiss_system: Sistema FAISS a guardar
        custom_path: Ruta personalizada (opcional)
        
    Returns:
        True si se guardó exitosamente
    """
    try:
        # Determinar ruta de guardado
        if custom_path:
            save_path = custom_path
        else:
            graphs_dir = STORAGE_CONFIG["graphs_dir"]
            os.makedirs(graphs_dir, exist_ok=True)
            save_path = os.path.join(graphs_dir, "faiss_system.pkl")
        
        # Guardar sistema completo
        with open(save_path, 'wb') as f:
            pickle.dump(faiss_system, f)
        
        print(f"💾 Sistema FAISS guardado: {save_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error guardando sistema FAISS: {e}")
        return False


def load_faiss_system(custom_path: str = None) -> Optional[TreeGraphRAG]:
    """
    Cargar sistema FAISS desde disco
    
    Args:
        custom_path: Ruta personalizada (opcional)
        
    Returns:
        Sistema FAISS cargado o None si falla
    """
    try:
        # Determinar ruta de carga
        if custom_path:
            load_path = custom_path
        else:
            graphs_dir = STORAGE_CONFIG["graphs_dir"]
            load_path = os.path.join(graphs_dir, "faiss_system.pkl")
        
        if not os.path.exists(load_path):
            print(f"⚠️ Sistema FAISS no encontrado: {load_path}")
            return None
        
        # Cargar sistema
        with open(load_path, 'rb') as f:
            faiss_system = pickle.load(f)
        
        print(f"📂 Sistema FAISS cargado: {load_path}")
        
        # Verificar que el índice esté construido
        if not faiss_system.is_built:
            print("🔄 Reconstruyendo índice FAISS...")
            faiss_system.build_index()
        
        faiss_system.print_system_summary()
        return faiss_system
        
    except Exception as e:
        print(f"❌ Error cargando sistema FAISS: {e}")
        return None


def migrate_hierarchical_to_faiss(hierarchical_path: str = None) -> bool:
    """
    Migrar desde grafo jerárquico a sistema FAISS
    
    Args:
        hierarchical_path: Ruta del grafo jerárquico (opcional)
        
    Returns:
        True si la migración fue exitosa
    """
    print("\n🔄 MIGRACIÓN: GRAFO JERÁRQUICO → SISTEMA FAISS")
    print("=" * 60)
    
    try:
        # 1. Cargar grafo jerárquico
        if hierarchical_path:
            load_path = hierarchical_path
        else:
            graphs_dir = STORAGE_CONFIG["graphs_dir"]
            load_path = os.path.join(graphs_dir, "document_graph_hierarchical.pkl")
        
        if not os.path.exists(load_path):
            print(f"❌ Grafo jerárquico no encontrado: {load_path}")
            return False
        
        print(f"📂 Cargando grafo jerárquico: {load_path}")
        with open(load_path, 'rb') as f:
            hierarchical_graph = pickle.load(f)
        
        # 2. Crear sistema FAISS
        faiss_system = create_faiss_system_from_hierarchical(hierarchical_graph)
        
        if not faiss_system.is_built:
            print("❌ Error creando sistema FAISS")
            return False
        
        # 3. Guardar sistema FAISS
        success = save_faiss_system(faiss_system)
        
        if success:
            print("\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
            print("💡 El sistema ahora usa FAISS para búsqueda por raíces")
            print("🚀 Uso: python3 query_faiss.py")
        
        return success
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_faiss_system(faiss_system: TreeGraphRAG) -> bool:
    """
    Verificar que el sistema FAISS esté funcionando correctamente
    
    Args:
        faiss_system: Sistema a verificar
        
    Returns:
        True si todas las verificaciones pasan
    """
    print("\n🔍 VERIFICANDO SISTEMA FAISS")
    print("-" * 30)
    
    checks = []
    
    # 1. Verificar que esté construido
    if faiss_system.is_built:
        checks.append("✅ Índice FAISS construido")
    else:
        checks.append("❌ Índice FAISS no construido")
        return False
    
    # 2. Verificar que tenga documentos
    stats = faiss_system.get_stats()
    if stats['total_documents'] > 0:
        checks.append(f"✅ Documentos indexados: {stats['total_documents']}")
    else:
        checks.append("❌ No hay documentos indexados")
        return False
    
    # 3. Verificar que las raíces tengan embeddings
    if stats['indexed_roots'] > 0:
        checks.append(f"✅ Raíces indexadas: {stats['indexed_roots']}")
    else:
        checks.append("❌ No hay raíces indexadas")
        return False
    
    # 4. Prueba de búsqueda
    try:
        test_results = faiss_system.search("test query", k=1)
        if test_results:
            checks.append("✅ Búsqueda de prueba exitosa")
        else:
            checks.append("⚠️ Búsqueda de prueba sin resultados")
    except Exception as e:
        checks.append(f"❌ Error en búsqueda de prueba: {e}")
        return False
    
    # Imprimir resultados
    for check in checks:
        print(check)
    
    print("\n🎉 Sistema FAISS verificado correctamente")
    return True