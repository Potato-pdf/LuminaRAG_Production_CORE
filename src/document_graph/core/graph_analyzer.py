import networkx as nx
from typing import List, Tuple, Dict, Optional

class GraphAnalyzer:
    
    def __init__(self, graph: nx.DiGraph):
        self._graph = graph

    def find_path(self, start_chunk: str, end_chunk: str) -> Optional[List[str]]: #Funcion para encontrar el camino mas corto entre 2 chunks
        try:
            path = nx.shortest_path(self._graph, start_chunk, end_chunk)
            return path
        except nx.NetworkXNoPath:
            return None
        except nx.NodeNotFound:
            return None
    
    def get_most_important_chunks(self, top_k: int = 5) -> List[Tuple[str, float]]:
        #| Obtiene los chunks mas importantes usando PageRank
        if self._graph.number_of_nodes() == 0:
            return []
        pagerank_scores = nx.pagerank(self._graph)
        sorted_chunks = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
        top_chunks = sorted_chunks[:top_k]
        
        #| Top {top_k} chunks más importantes calculados
        return top_chunks
    
    def get_chunk_neighbors(self, chunk_id: str, radius: int = 1) -> List[str]:
        #| Obtiene vecinos de un chunk dentro del radio especificado
        if chunk_id not in self._graph:
            return []
            
        ego_graph = nx.ego_graph(self._graph, chunk_id, radius=radius)
        neighbors = list(ego_graph.nodes())
        # Remover el chunk central
        if chunk_id in neighbors:
            neighbors.remove(chunk_id)
        #| Vecinos de {chunk_id} calculados (radio {radius})
        return neighbors
    
    def get_stats(self) -> Dict:#Obtiene estadisticas del grafo
        total_chunks = self._graph.number_of_nodes()
        total_connections = self._graph.number_of_edges()
        stats = {
            'total_chunks': total_chunks,
            'total_connections': total_connections,
            'density': nx.density(self._graph) if total_chunks > 0 else 0.0,
            'is_connected': nx.is_strongly_connected(self._graph) if total_chunks > 0 else False,
            'average_degree': (2 * total_connections / total_chunks) if total_chunks > 0 else 0.0
        }
        
        documents = set()# Contar documentos únicos
        for node_data in self._graph.nodes(data=True):
            file_name = node_data[1].get('metadata', {}).get('file_name')
            if file_name:
                documents.add(file_name)
        stats['documents_count'] = len(documents)
        self._print_stats(stats)
        return stats
    
    def _print_stats(self, stats: Dict) -> None:
        #| Estadísticas del grafo:
        #| Total chunks: {stats['total_chunks']}
        #| Total conexiones: {stats['total_connections']}
        #| Documentos: {stats['documents_count']}
        #| Densidad: {stats['density']:.3f}
        #| Fuertemente conectado: {stats['is_connected']}
        #| Grado promedio: {stats['average_degree']:.3f}
        pass

    def analyze_connectivity(self, chunk_id: str) -> Dict:#Analiza la conectividad de un chunk especifico
        if chunk_id not in self._graph:
            return {'error': f'Chunk {chunk_id} no encontrado'}
        in_degree = self._graph.in_degree(chunk_id)
        out_degree = self._graph.out_degree(chunk_id)
        centrality_scores = {}
        if self._graph.number_of_nodes() > 1:
            try:
                centrality_scores = {
                    'pagerank': nx.pagerank(self._graph).get(chunk_id, 0),
                    'betweenness': nx.betweenness_centrality(self._graph).get(chunk_id, 0),
                    'degree': nx.degree_centrality(self._graph).get(chunk_id, 0)
                }
            except:
                centrality_scores = {'pagerank': 0, 'betweenness': 0, 'degree': 0}
        
        analysis = {
            'chunk_id': chunk_id,
            'in_degree': in_degree,
            'out_degree': out_degree,
            'total_degree': in_degree + out_degree,
            'centrality': centrality_scores
        }
        return analysis
