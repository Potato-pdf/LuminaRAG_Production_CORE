import networkx as nx
import json
from typing import Dict
class GraphExporter:
    
    def __init__(self, graph: nx.DiGraph):
        self._graph = graph
    
    def save_graph(self, filename: str) -> None:#guarda el grafo en multiples formatos
        try:
            self.save_as_graphml(filename)
            self.save_as_json(filename)
            print(f"💾 Grafo guardado como {filename}.graphml y {filename}.json")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
    
    def save_as_graphml(self, filename: str) -> None:
        # Crear versión simplificada para evitar problemas con metadatos complejos
        export_graph = nx.DiGraph()
        
        for node_id in self._graph.nodes():
            node_data = self._graph.nodes[node_id]
            export_graph.add_node(
                node_id,
                content_preview=self._truncate_content(node_data['content']),
                file_name=node_data['metadata'].get('file_name', 'unknown')
            )
        
        # Copiar conexiones con sus pesos
        for edge in self._graph.edges(data=True):
            export_graph.add_edge(edge[0], edge[1], **edge[2])
        
        nx.write_graphml(export_graph, filename + ".graphml")
    
    def save_as_json(self, filename: str) -> None:
        data = {
            'metadata': self._create_metadata(),
            'nodes': self._export_nodes(),
            'edges': self._export_edges()
        }
        
        with open(filename + ".json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_to_dict(self) -> Dict:
        return {
            'metadata': self._create_metadata(),
            'nodes': self._export_nodes(),
            'edges': self._export_edges()
        }
    
    def _create_metadata(self) -> Dict:
        """Crear metadatos del grafo"""
        return {
            'total_chunks': self._graph.number_of_nodes(),
            'total_connections': self._graph.number_of_edges(),
            'density': nx.density(self._graph),
            'created_by': 'SimpleDocumentGraph',
            'format_version': '1.0'
        }
    
    def _export_nodes(self) -> list:
        """Exportar nodos con sus datos"""
        nodes = []
        for node_id in self._graph.nodes():
            node_data = self._graph.nodes[node_id]
            nodes.append({
                'id': node_id,
                'content': node_data['content'],
                'content_preview': self._truncate_content(node_data['content']),
                'metadata': node_data['metadata']
            })
        return nodes
    
    def _export_edges(self) -> list:
        """Exportar conexiones con sus pesos"""
        edges = []
        for edge in self._graph.edges(data=True):
            edges.append({
                'from': edge[0],
                'to': edge[1],
                'weight': edge[2].get('weight', 1.0)
            })
        return edges
    
    def _truncate_content(self, content: str, max_length: int = 100) -> str:
        """Truncar contenido para preview"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."
    
    def save_subset(self, filename: str, chunk_ids: list[str]) -> None:
        """
        Guardar un subconjunto del grafo.
        
        Args:
            filename: Nombre del archivo
            chunk_ids: Lista de IDs de chunks a incluir
        """
        subgraph = self._graph.subgraph(chunk_ids)
        exporter = GraphExporter(subgraph)
        exporter.save_graph(filename)
        print(f"💾 Subgrafo guardado: {len(chunk_ids)} chunks en {filename}")
    
    def export_statistics_report(self, filename: str) -> None:
        """
        Exportar reporte de estadísticas en formato texto.
        
        Args:
            filename: Nombre del archivo de reporte
        """
        from .graph_analyzer import GraphAnalyzer
        
        analyzer = GraphAnalyzer(self._graph)
        stats = analyzer.get_stats()
        
        report = f"""
Reporte de Estadísticas del Grafo
=================================

Información General:
- Total de chunks: {stats['total_chunks']}
- Total de conexiones: {stats['total_connections']}  
- Documentos procesados: {stats['documents_count']}

Métricas de Conectividad:
- Densidad del grafo: {stats['density']:.3f}
- Fuertemente conectado: {stats['is_connected']}
- Grado promedio: {stats['average_degree']:.3f}

Generado por: SimpleDocumentGraph
        """.strip()
        
        with open(filename + "_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 Reporte de estadísticas guardado en {filename}_report.txt")
