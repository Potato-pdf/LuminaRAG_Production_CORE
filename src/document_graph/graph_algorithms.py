"""
Algoritmos de análisis y búsqueda para grafos dirigidos de documentos.
Incluye búsquedas, análisis de centralidad, detección de ciclos, etc.
"""
from typing import List, Dict, Set, Optional, Tuple
from collections import deque, defaultdict
import heapq
from .graph_core import DocumentGraphCore


class GraphAnalyzer:
    """Clase para análisis avanzado de grafos dirigidos"""
    
    def __init__(self, graph: DocumentGraphCore):
        self.graph = graph
    
    def bfs_traversal(self, start_vertex: str, max_depth: int = 3) -> List[str]:
        """Búsqueda en anchura (BFS) desde un vértice hasta cierta profundidad"""
        if start_vertex not in self.graph.graph_dict:
            return []
        
        visited = set()
        queue = deque([(start_vertex, 0)])  # (vertex, depth)
        result = []
        
        while queue:
            vertex, depth = queue.popleft()
            if vertex in visited or depth > max_depth:
                continue
                
            visited.add(vertex)
            result.append(vertex)
            
            # Agregar vecinos a la cola
            for neighbor_info in self.graph.graph_dict[vertex]:
                neighbor = neighbor_info['vertex']
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
        
        return result
    
    def find_shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """Encontrar el camino más corto entre dos vértices usando Dijkstra"""
        if start not in self.graph.graph_dict or end not in self.graph.graph_dict:
            return None
        
        distances = {vertex: float('inf') for vertex in self.graph.graph_dict}
        distances[start] = 0
        previous = {}
        pq = [(0, start)]
        
        while pq:
            current_distance, current = heapq.heappop(pq)
            
            if current == end:
                break
                
            if current_distance > distances[current]:
                continue
            
            for neighbor_info in self.graph.graph_dict[current]:
                neighbor = neighbor_info['vertex']
                weight = neighbor_info['weight']
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruir el camino
        if distances[end] == float('inf'):
            return None
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous.get(current)
        
        return path[::-1]
    
    def get_connected_components(self) -> List[List[str]]:
        """Encontrar todos los componentes conectados del grafo"""
        visited = set()
        components = []
        
        for vertex in self.graph.graph_dict:
            if vertex not in visited:
                component = []
                stack = [vertex]
                
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        component.append(current)
                        
                        for neighbor_info in self.graph.graph_dict[current]:
                            neighbor = neighbor_info['vertex']
                            if neighbor not in visited:
                                stack.append(neighbor)
                
                components.append(component)
        
        return components
    
    def calculate_centrality_measures(self) -> Dict[str, Dict[str, float]]:
        """Calcular medidas de centralidad para grafos dirigidos"""
        centralities = {}
        
        for vertex in self.graph.graph_dict:
            # Centralidad de grado de salida (out-degree)
            out_degree = len(self.graph.graph_dict[vertex])
            out_degree_centrality = out_degree / (len(self.graph.graph_dict) - 1) if len(self.graph.graph_dict) > 1 else 0
            
            # Centralidad de grado de entrada (in-degree)
            in_degree = len(self.graph.get_predecessors(vertex))
            in_degree_centrality = in_degree / (len(self.graph.graph_dict) - 1) if len(self.graph.graph_dict) > 1 else 0
            
            # Centralidad de cercanía (basada en caminos más cortos salientes)
            total_distance = 0
            reachable_vertices = 0
            
            for other_vertex in self.graph.graph_dict:
                if other_vertex != vertex:
                    path = self.find_shortest_path(vertex, other_vertex)
                    if path:
                        total_distance += len(path) - 1
                        reachable_vertices += 1
            
            closeness_centrality = reachable_vertices / total_distance if total_distance > 0 else 0
            
            centralities[vertex] = {
                'out_degree_centrality': out_degree_centrality,
                'in_degree_centrality': in_degree_centrality,
                'closeness_centrality': closeness_centrality,
                'out_degree': out_degree,
                'in_degree': in_degree,
                'total_degree': out_degree + in_degree
            }
        
        return centralities
    
    def topological_sort(self) -> List[str]:
        """
        Ordenamiento topológico del grafo dirigido
        Útil para determinar un orden válido de procesamiento de chunks
        """
        in_degree = {vertex: 0 for vertex in self.graph.graph_dict}
        
        # Calcular grados de entrada
        for vertex in self.graph.graph_dict:
            for neighbor_info in self.graph.graph_dict[vertex]:
                in_degree[neighbor_info['vertex']] += 1
        
        # Queue con vértices de grado de entrada 0
        queue = deque([vertex for vertex in in_degree if in_degree[vertex] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Reducir grado de entrada de sucesores
            for neighbor_info in self.graph.graph_dict[current]:
                neighbor = neighbor_info['vertex']
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Verificar si hay ciclos
        if len(result) != len(self.graph.graph_dict):
            raise ValueError("El grafo contiene ciclos - no se puede hacer ordenamiento topológico")
        
        return result
    
    def detect_cycles(self) -> List[List[str]]:
        """Detectar ciclos en el grafo dirigido"""
        white = set(self.graph.graph_dict.keys())  # No visitado
        gray = set()   # En proceso
        black = set()  # Completado
        cycles = []
        
        def dfs(vertex, path):
            if vertex in gray:  # Encontramos un ciclo
                cycle_start = path.index(vertex)
                cycles.append(path[cycle_start:] + [vertex])
                return
            
            if vertex in black:
                return
            
            white.discard(vertex)
            gray.add(vertex)
            path.append(vertex)
            
            for neighbor_info in self.graph.graph_dict[vertex]:
                neighbor = neighbor_info['vertex']
                dfs(neighbor, path.copy())
            
            gray.discard(vertex)
            black.add(vertex)
        
        for vertex in list(white):
            if vertex in white:
                dfs(vertex, [])
        
        return cycles
    
    def find_critical_edges(self) -> List[Tuple[str, str]]:
        """
        Para grafos dirigidos, encontrar aristas críticas cuya eliminación 
        afecta significativamente la conectividad
        """
        critical_edges = []
        
        # Para cada arista, verificar si su eliminación desconecta componentes
        for vertex in self.graph.graph_dict:
            for neighbor_info in self.graph.graph_dict[vertex]:
                neighbor = neighbor_info['vertex']
                
                # Temporalmente remover la arista
                original_neighbors = self.graph.graph_dict[vertex][:]
                self.graph.graph_dict[vertex] = [n for n in self.graph.graph_dict[vertex] 
                                               if n['vertex'] != neighbor]
                
                # Verificar si el grafo sigue fuertemente conectado
                if not self._is_strongly_connected():
                    critical_edges.append((vertex, neighbor))
                
                # Restaurar la arista
                self.graph.graph_dict[vertex] = original_neighbors
        
        return critical_edges
    
    def _is_strongly_connected(self) -> bool:
        """Verificar si el grafo dirigido es fuertemente conectado"""
        if not self.graph.graph_dict:
            return True
        
        # Verificar que desde cualquier vértice se puede llegar a todos los demás
        start_vertex = next(iter(self.graph.graph_dict))
        visited = set()
        
        def dfs(vertex):
            visited.add(vertex)
            for neighbor_info in self.graph.graph_dict[vertex]:
                neighbor = neighbor_info['vertex']
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(start_vertex)
        
        return len(visited) == len(self.graph.graph_dict)
