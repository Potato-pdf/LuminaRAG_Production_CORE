"""
Core del sistema de grafos dirigidos para Document Graph Augmentation (DGA).
Contiene las clases base para vertices, aristas y la estructura principal del grafo.
"""
from typing import List, Dict, Set, Optional, Any, Tuple
from collections import deque
import json


class Edge:
    """Clase que representa una arista dirigida en el grafo"""
    
    def __init__(self, v1: str, v2: str, weight: float = 1.0):
        self.v1 = v1  # Vértice de inicio
        self.v2 = v2  # Vértice de fin
        self.weight = weight  # Peso de la arista
    
    def get_v1(self) -> str:
        return self.v1
    
    def get_v2(self) -> str:
        return self.v2
    
    def get_weight(self) -> float:
        return self.weight
    
    def __str__(self) -> str:
        return f"{self.v1} -> {self.v2} (weight: {self.weight})"


class Vertex:
    """Clase que representa un vértice (chunk) en el grafo"""
    
    def __init__(self, chunk_id: str, chunk_content: str, metadata: Dict = None):
        self.chunk_id = chunk_id
        self.chunk_content = chunk_content
        self.metadata = metadata or {}
    
    def get_chunk_id(self) -> str:
        return self.chunk_id
    
    def get_chunk_content(self) -> str:
        return self.chunk_content
    
    def get_metadata(self) -> Dict:
        return self.metadata
    
    def __str__(self) -> str:
        return f"Vertex({self.chunk_id}): {self.chunk_content[:50]}..."


class DocumentGraphCore:
    """Clase principal del grafo dirigido para documentos"""
    
    def __init__(self, directed: bool = True):
        self.graph_dict = {}  # Diccionario que maneja el grafo
        self.directed = directed  # Siempre True para reconstrucción de documentos
        self.vertex_metadata = {}  # Metadatos adicionales por vértice
        self.document_structure = {}  # Estructura del documento original
        
    def add_vertex(self, vertex_id: str, metadata: Dict = None) -> str:
        """Agregar un vértice al grafo"""
        if vertex_id in self.graph_dict:
            return "Vertex is already present."
        self.graph_dict[vertex_id] = []
        self.vertex_metadata[vertex_id] = metadata or {}
        return "Vertex added successfully."
    
    def add_edge(self, edge: Edge, weight: float = 1.0, edge_type: str = "semantic") -> str:
        """
        Agregar una arista dirigida al grafo con peso y tipo
        
        Args:
            edge: Objeto Edge
            weight: Peso de la arista (relevancia/similitud)
            edge_type: Tipo de relación ("sequential", "semantic", "reference", "continuation")
        """
        v1 = edge.get_v1()
        v2 = edge.get_v2()
        
        if v1 not in self.graph_dict:
            return "Vertex 1 not present."
        if v2 not in self.graph_dict:
            return "Vertex 2 not present."
            
        # Agregar arista dirigida con metadatos
        edge_info = {
            'vertex': v2, 
            'weight': weight,
            'type': edge_type,
            'creation_order': len(self.graph_dict[v1])  # Orden de creación
        }
        self.graph_dict[v1].append(edge_info)
        
        return "Directed edge added successfully."
    
    def add_sequential_edges(self, chunk_sequence: List[str], weight: float = 1.0) -> str:
        """
        Agregar aristas secuenciales para mantener el orden del documento
        
        Args:
            chunk_sequence: Lista ordenada de chunk_ids como aparecen en el documento
            weight: Peso para las aristas secuenciales
        """
        for i in range(len(chunk_sequence) - 1):
            current_chunk = chunk_sequence[i]
            next_chunk = chunk_sequence[i + 1]
            
            edge = Edge(current_chunk, next_chunk, weight)
            self.add_edge(edge, weight, "sequential")
            
        # Guardar la secuencia original para reconstrucción
        document_id = f"doc_{len(self.document_structure)}"
        self.document_structure[document_id] = chunk_sequence
        
        return f"Sequential edges added for document {document_id}"
    
    def get_neighbors(self, vertex_id: str) -> List[Dict]:
        """Obtener vecinos de un vértice"""
        return self.graph_dict.get(vertex_id, [])
    
    def get_vertex_count(self) -> int:
        """Número total de vértices"""
        return len(self.graph_dict)
    
    def get_edge_count(self) -> int:
        """Número total de aristas dirigidas"""
        return sum(len(neighbors) for neighbors in self.graph_dict.values())
    
    def get_successors(self, vertex_id: str, edge_type: str = None) -> List[Dict]:
        """Obtener sucesores de un vértice (aristas salientes)"""
        neighbors = self.graph_dict.get(vertex_id, [])
        if edge_type:
            return [n for n in neighbors if n.get('type') == edge_type]
        return neighbors
    
    def get_predecessors(self, vertex_id: str, edge_type: str = None) -> List[str]:
        """Obtener predecesores de un vértice (aristas entrantes)"""
        predecessors = []
        for source, neighbors in self.graph_dict.items():
            for neighbor_info in neighbors:
                if neighbor_info['vertex'] == vertex_id:
                    if not edge_type or neighbor_info.get('type') == edge_type:
                        predecessors.append(source)
        return predecessors
    
    def export_to_json(self, filepath: str):
        """Exportar el grafo a JSON"""
        export_data = {
            'directed': self.directed,
            'vertices': list(self.graph_dict.keys()),
            'edges': [],
            'metadata': self.vertex_metadata,
            'document_structure': self.document_structure
        }
        
        for vertex, neighbors in self.graph_dict.items():
            for neighbor_info in neighbors:
                export_data['edges'].append({
                    'from': vertex,
                    'to': neighbor_info['vertex'],
                    'weight': neighbor_info['weight'],
                    'type': neighbor_info.get('type', 'unknown'),
                    'creation_order': neighbor_info.get('creation_order', 0)
                })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def load_from_json(self, filepath: str):
        """Cargar el grafo desde JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.directed = data.get('directed', True)
        self.graph_dict = {vertex: [] for vertex in data['vertices']}
        self.vertex_metadata = data.get('metadata', {})
        self.document_structure = data.get('document_structure', {})
        
        for edge_data in data['edges']:
            edge_obj = Edge(edge_data['from'], edge_data['to'])
            self.add_edge(
                edge_obj, 
                edge_data.get('weight', 1.0),
                edge_data.get('type', 'semantic')
            )
