"""
Document Graph Augmentation (DGA) - Implementación personalizada
Sistema de grafos para mejorar la recuperación contextual en RAG
"""
import json
from typing import List, Dict, Set, Optional, Any, Tuple
from collections import deque, defaultdict
import heapq
from llama_index.core.schema import Node

class DocumentGraphAugmentation:
    def __init__(self, directed: bool = True):  # Por defecto dirigido para reconstrucción de documentos
        self.graph_dict = {}  # Diccionario que maneja el grafo
        self.directed = directed  # Siempre True para reconstrucción de documentos
        self.vertex_metadata = {}  # Metadatos adicionales por vértice
        self.document_structure = {}  # Estructura del documento original
        
    def add_vertex(self, vertex_id, metadata: Dict = None):
        """Agregar un vértice al grafo"""
        if vertex_id in self.graph_dict:
            return "Vertex is already present."
        self.graph_dict[vertex_id] = []
        self.vertex_metadata[vertex_id] = metadata or {}
        return "Vertex added successfully."
    
    def add_edge(self, edge, weight: float = 1.0, edge_type: str = "semantic"):
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
    
    def add_sequential_edges(self, chunk_sequence: List[str], weight: float = 1.0):
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
    
    def get_neighbors(self, vertex_id) -> List[Dict]:
        """Obtener vecinos de un vértice"""
        return self.graph_dict.get(vertex_id, [])
    
    def get_vertex_count(self) -> int:
        """Número total de vértices"""
        return len(self.graph_dict)
    
    def get_edge_count(self) -> int:
        """Número total de aristas dirigidas"""
        return sum(len(neighbors) for neighbors in self.graph_dict.values())
    
    # === FUNCIONALIDADES ESPECÍFICAS PARA DOCUMENTOS DIRIGIDOS ===
    
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
    
    def reconstruct_document_path(self, start_chunk: str, document_id: str = None) -> List[str]:
        """
        Reconstruir el camino de un documento siguiendo las aristas secuenciales
        
        Args:
            start_chunk: Chunk inicial del documento
            document_id: ID del documento específico (opcional)
            
        Returns:
            Lista ordenada de chunks que forman el documento
        """
        if document_id and document_id in self.document_structure:
            return self.document_structure[document_id]
        
        # Reconstruir siguiendo aristas secuenciales
        path = [start_chunk]
        current = start_chunk
        visited = set([start_chunk])
        
        while True:
            # Buscar siguiente chunk secuencial
            sequential_successors = self.get_successors(current, "sequential")
            
            if not sequential_successors:
                break
                
            # Tomar el sucesor con mayor peso o el primero en orden de creación
            next_chunk_info = max(sequential_successors, 
                                key=lambda x: (x['weight'], -x['creation_order']))
            next_chunk = next_chunk_info['vertex']
            
            if next_chunk in visited:  # Evitar ciclos
                break
                
            path.append(next_chunk)
            visited.add(next_chunk)
            current = next_chunk
        
        return path
    
    def find_document_start_chunks(self) -> List[str]:
        """Encontrar chunks que pueden ser inicio de documentos (sin predecesores secuenciales)"""
        start_chunks = []
        
        for vertex_id in self.graph_dict:
            sequential_predecessors = self.get_predecessors(vertex_id, "sequential")
            if not sequential_predecessors:
                start_chunks.append(vertex_id)
        
        return start_chunks
    
    def get_contextual_chunks(self, chunk_id: str, context_radius: int = 2) -> Dict[str, List[str]]:
        """
        Obtener chunks contextuales alrededor de un chunk dado
        
        Args:
            chunk_id: ID del chunk central
            context_radius: Radio de contexto (chunks antes y después)
            
        Returns:
            Diccionario con chunks anteriores, el chunk actual, y chunks posteriores
        """
        result = {
            'before': [],
            'current': chunk_id,
            'after': []
        }
        
        # Obtener chunks anteriores siguiendo predecesores secuenciales
        current = chunk_id
        for _ in range(context_radius):
            predecessors = self.get_predecessors(current, "sequential")
            if predecessors:
                prev_chunk = predecessors[0]  # Tomar el primer predecesor
                result['before'].insert(0, prev_chunk)
                current = prev_chunk
            else:
                break
        
        # Obtener chunks posteriores siguiendo sucesores secuenciales
        current = chunk_id
        for _ in range(context_radius):
            successors = self.get_successors(current, "sequential")
            if successors:
                next_chunk = successors[0]['vertex']  # Tomar el primer sucesor
                result['after'].append(next_chunk)
                current = next_chunk
            else:
                break
        
        return result
    
    def topological_sort(self) -> List[str]:
        """
        Ordenamiento topológico del grafo dirigido
        Útil para determinar un orden válido de procesamiento de chunks
        """
        in_degree = {vertex: 0 for vertex in self.graph_dict}
        
        # Calcular grados de entrada
        for vertex in self.graph_dict:
            for neighbor_info in self.graph_dict[vertex]:
                in_degree[neighbor_info['vertex']] += 1
        
        # Queue con vértices de grado de entrada 0
        queue = deque([vertex for vertex in in_degree if in_degree[vertex] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Reducir grado de entrada de sucesores
            for neighbor_info in self.graph_dict[current]:
                neighbor = neighbor_info['vertex']
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Verificar si hay ciclos
        if len(result) != len(self.graph_dict):
            raise ValueError("El grafo contiene ciclos - no se puede hacer ordenamiento topológico")
        
        return result
    
    def detect_cycles(self) -> List[List[str]]:
        """Detectar ciclos en el grafo dirigido"""
        white = set(self.graph_dict.keys())  # No visitado
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
            
            for neighbor_info in self.graph_dict[vertex]:
                neighbor = neighbor_info['vertex']
                dfs(neighbor, path.copy())
            
            gray.discard(vertex)
            black.add(vertex)
        
        for vertex in list(white):
            if vertex in white:
                dfs(vertex, [])
        
        return cycles

    
    # === FUNCIONALIDADES AVANZADAS ===
    
    def bfs_traversal(self, start_vertex, max_depth: int = 3) -> List[str]:
        """Búsqueda en anchura (BFS) desde un vértice hasta cierta profundidad"""
        if start_vertex not in self.graph_dict:
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
            for neighbor_info in self.graph_dict[vertex]:
                neighbor = neighbor_info['vertex']
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
        
        return result
    
    def find_shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """Encontrar el camino más corto entre dos vértices usando Dijkstra"""
        if start not in self.graph_dict or end not in self.graph_dict:
            return None
        
        distances = {vertex: float('inf') for vertex in self.graph_dict}
        distances[start] = 0
        previous = {}
        pq = [(0, start)]
        
        while pq:
            current_distance, current = heapq.heappop(pq)
            
            if current == end:
                break
                
            if current_distance > distances[current]:
                continue
            
            for neighbor_info in self.graph_dict[current]:
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
        
        for vertex in self.graph_dict:
            if vertex not in visited:
                component = []
                stack = [vertex]
                
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        component.append(current)
                        
                        for neighbor_info in self.graph_dict[current]:
                            neighbor = neighbor_info['vertex']
                            if neighbor not in visited:
                                stack.append(neighbor)
                
                components.append(component)
        
        return components
    
    def calculate_centrality_measures(self) -> Dict[str, Dict[str, float]]:
        """Calcular medidas de centralidad para grafos dirigidos"""
        centralities = {}
        
        for vertex in self.graph_dict:
            # Centralidad de grado de salida (out-degree)
            out_degree = len(self.graph_dict[vertex])
            out_degree_centrality = out_degree / (len(self.graph_dict) - 1) if len(self.graph_dict) > 1 else 0
            
            # Centralidad de grado de entrada (in-degree)
            in_degree = len(self.get_predecessors(vertex))
            in_degree_centrality = in_degree / (len(self.graph_dict) - 1) if len(self.graph_dict) > 1 else 0
            
            # Centralidad de cercanía (basada en caminos más cortos salientes)
            total_distance = 0
            reachable_vertices = 0
            
            for other_vertex in self.graph_dict:
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
    
    def find_bridges(self) -> List[Tuple[str, str]]:
        """
        Para grafos dirigidos, encontrar aristas críticas cuya eliminación 
        afecta significativamente la conectividad
        """
        critical_edges = []
        
        # Para cada arista, verificar si su eliminación desconecta componentes
        for vertex in self.graph_dict:
            for neighbor_info in self.graph_dict[vertex]:
                neighbor = neighbor_info['vertex']
                
                # Temporalmente remover la arista
                self.graph_dict[vertex] = [n for n in self.graph_dict[vertex] 
                                         if n['vertex'] != neighbor]
                
                # Verificar si el grafo sigue fuertemente conectado
                if not self._is_strongly_connected():
                    critical_edges.append((vertex, neighbor))
                
                # Restaurar la arista
                self.graph_dict[vertex].append(neighbor_info)
        
        return critical_edges
    
    def _is_strongly_connected(self) -> bool:
        """Verificar si el grafo dirigido es fuertemente conectado"""
        if not self.graph_dict:
            return True
        
        # Verificar que desde cualquier vértice se puede llegar a todos los demás
        start_vertex = next(iter(self.graph_dict))
        visited = set()
        
        def dfs(vertex):
            visited.add(vertex)
            for neighbor_info in self.graph_dict[vertex]:
                neighbor = neighbor_info['vertex']
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(start_vertex)
        
        return len(visited) == len(self.graph_dict)
    
    def export_to_json(self, filepath: str):
        """Exportar el grafo a JSON"""
        export_data = {
            'directed': self.directed,
            'vertices': list(self.graph_dict.keys()),
            'edges': [],
            'metadata': self.vertex_metadata
        }
        
        for vertex, neighbors in self.graph_dict.items():
            for neighbor_info in neighbors:
                export_data['edges'].append({
                    'from': vertex,
                    'to': neighbor_info['vertex'],
                    'weight': neighbor_info['weight']
                })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def load_from_json(self, filepath: str):
        """Cargar el grafo desde JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.directed = data.get('directed', False)
        self.graph_dict = {vertex: [] for vertex in data['vertices']}
        self.vertex_metadata = data.get('metadata', {})
        
        for edge_data in data['edges']:
            edge_obj = Edge(edge_data['from'], edge_data['to'])
            self.add_edge(edge_obj, edge_data.get('weight', 1.0))


class Edge:
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


# === INTEGRACIÓN CON RAG PARA RECONSTRUCCIÓN DE DOCUMENTOS ===

class RAGDocumentGraphIntegration:
    """Clase para integrar el grafo dirigido con el sistema RAG para reconstrucción de documentos"""
    
    def __init__(self, graph: DocumentGraphAugmentation):
        self.graph = graph
    
    def build_document_graph_from_nodes(self, nodes: List[Node], 
                                      similarity_threshold: float = 0.7,
                                      preserve_document_order: bool = True):
        """
        Construir grafo dirigido a partir de nodos de LlamaIndex preservando orden de documento
        
        Args:
            nodes: Lista de nodos de LlamaIndex
            similarity_threshold: Umbral para aristas semánticas
            preserve_document_order: Si preservar el orden original del documento
        """
        # Agregar todos los nodos como vértices
        for node in nodes:
            metadata = {
                'content': node.get_content(),
                'node_id': node.node_id,
                'metadata': node.metadata,
                'document_position': self._extract_document_position(node)
            }
            self.graph.add_vertex(node.node_id, metadata)
        
        if preserve_document_order:
            # Agrupar nodos por documento y crear aristas secuenciales
            docs_nodes = self._group_nodes_by_document(nodes)
            
            for doc_id, doc_nodes in docs_nodes.items():
                # Ordenar nodos por posición en el documento
                doc_nodes.sort(key=lambda n: self._extract_document_position(n))
                
                # Crear secuencia de chunks para este documento
                chunk_sequence = [node.node_id for node in doc_nodes]
                self.graph.add_sequential_edges(chunk_sequence, weight=1.0)
        
        # Crear aristas semánticas basadas en similitud
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes[i+1:], i+1):
                similarity = self._calculate_similarity(node1, node2)
                
                if similarity > similarity_threshold:
                    # Crear arista dirigida basada en posición en el documento
                    pos1 = self._extract_document_position(node1)
                    pos2 = self._extract_document_position(node2)
                    
                    if pos1 < pos2:
                        edge = Edge(node1.node_id, node2.node_id, similarity)
                        self.graph.add_edge(edge, similarity, "semantic")
                    else:
                        edge = Edge(node2.node_id, node1.node_id, similarity)
                        self.graph.add_edge(edge, similarity, "semantic")
    
    def _group_nodes_by_document(self, nodes: List[Node]) -> Dict[str, List[Node]]:
        """Agrupar nodos por documento de origen"""
        docs = defaultdict(list)
        
        for node in nodes:
            # Extraer ID del documento desde metadatos o nombre del archivo
            doc_id = node.metadata.get('file_name', 'unknown_doc')
            docs[doc_id].append(node)
        
        return dict(docs)
    
    def _extract_document_position(self, node: Node) -> int:
        """Extraer la posición del nodo en el documento original"""
        # Intentar extraer posición desde metadatos
        position = node.metadata.get('position', 0)
        if isinstance(position, int):
            return position
        
        # Fallback: usar hash del contenido para ordenamiento consistente
        return hash(node.get_content()[:100]) % 1000000
    
    def _calculate_similarity(self, node1: Node, node2: Node) -> float:
        """Calcular similitud entre dos nodos (placeholder - implementa tu lógica)"""
        # Aquí puedes implementar diferentes métodos:
        # - Similitud de embeddings
        # - Similitud de texto usando TF-IDF
        # - Similitud basada en metadatos
        
        # Placeholder: similitud basada en palabras comunes
        content1 = set(node1.get_content().lower().split())
        content2 = set(node2.get_content().lower().split())
        
        if not content1 or not content2:
            return 0.0
        
        intersection = len(content1.intersection(content2))
        union = len(content1.union(content2))
        
        return intersection / union if union > 0 else 0.0
    
    def enhanced_document_retrieval(self, query_node_id: str, 
                                  context_radius: int = 2,
                                  include_semantic: bool = True,
                                  max_chunks: int = 10) -> Dict[str, Any]:
        """
        Recuperación mejorada que reconstruye contexto de documento
        
        Args:
            query_node_id: ID del nodo de consulta
            context_radius: Radio de contexto secuencial
            include_semantic: Si incluir chunks relacionados semánticamente
            max_chunks: Máximo número de chunks a retornar
            
        Returns:
            Diccionario con chunks organizados por tipo de relación
        """
        result = {
            'sequential_context': {},
            'semantic_related': [],
            'document_path': [],
            'centrality_scores': {}
        }
        
        # Obtener contexto secuencial
        result['sequential_context'] = self.graph.get_contextual_chunks(
            query_node_id, context_radius
        )
        
        # Obtener camino completo del documento
        try:
            result['document_path'] = self.graph.reconstruct_document_path(query_node_id)
        except:
            result['document_path'] = [query_node_id]
        
        # Obtener chunks relacionados semánticamente si se solicita
        if include_semantic:
            semantic_successors = self.graph.get_successors(query_node_id, "semantic")
            semantic_predecessors = self.graph.get_predecessors(query_node_id, "semantic")
            
            all_semantic = semantic_successors + [{'vertex': p, 'weight': 0.5} 
                                                for p in semantic_predecessors]
            
            # Ordenar por peso y tomar los mejores
            all_semantic.sort(key=lambda x: x.get('weight', 0), reverse=True)
            result['semantic_related'] = [item['vertex'] for item in all_semantic[:max_chunks//2]]
        
        # Calcular scores de centralidad para priorización
        centralities = self.graph.calculate_centrality_measures()
        result['centrality_scores'] = centralities.get(query_node_id, {})
        
        return result
    
    def reconstruct_full_document(self, start_chunk_id: str) -> List[Dict[str, Any]]:
        """
        Reconstruir un documento completo desde un chunk inicial
        
        Args:
            start_chunk_id: ID del chunk inicial
            
        Returns:
            Lista ordenada de chunks con metadatos para reconstruir el documento
        """
        # Encontrar el verdadero inicio del documento
        document_starts = self.graph.find_document_start_chunks()
        
        # Si el chunk dado no es inicio, buscar el inicio de su documento
        if start_chunk_id not in document_starts:
            # Buscar hacia atrás siguiendo aristas secuenciales
            current = start_chunk_id
            while True:
                predecessors = self.graph.get_predecessors(current, "sequential")
                if not predecessors:
                    start_chunk_id = current
                    break
                current = predecessors[0]
        
        # Reconstruir el documento completo
        document_path = self.graph.reconstruct_document_path(start_chunk_id)
        
        # Enriquecer con metadatos
        enriched_chunks = []
        for i, chunk_id in enumerate(document_path):
            chunk_info = {
                'chunk_id': chunk_id,
                'position': i,
                'content': self.graph.vertex_metadata.get(chunk_id, {}).get('content', ''),
                'metadata': self.graph.vertex_metadata.get(chunk_id, {}),
                'is_start': i == 0,
                'is_end': i == len(document_path) - 1
            }
            enriched_chunks.append(chunk_info)
        
        return enriched_chunks