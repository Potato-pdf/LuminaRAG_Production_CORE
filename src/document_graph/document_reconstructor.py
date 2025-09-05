"""
Funcionalidades específicas para reconstrucción y navegación de documentos.
Maneja la lógica de reconstruir documentos a partir de chunks y navegar por su estructura.
"""
from typing import List, Dict, Set, Optional, Any
from .graph_core import DocumentGraphCore


class DocumentReconstructor:
    """Clase especializada en reconstruir y navegar documentos usando el grafo"""
    
    def __init__(self, graph: DocumentGraphCore):
        self.graph = graph
    
    def reconstruct_document_path(self, start_chunk: str, document_id: str = None) -> List[str]:
        """
        Reconstruir el camino de un documento siguiendo las aristas secuenciales
        
        Args:
            start_chunk: Chunk inicial del documento
            document_id: ID del documento específico (opcional)
            
        Returns:
            Lista ordenada de chunks que forman el documento
        """
        if document_id and document_id in self.graph.document_structure:
            return self.graph.document_structure[document_id]
        
        # Reconstruir siguiendo aristas secuenciales
        path = [start_chunk]
        current = start_chunk
        visited = set([start_chunk])
        
        while True:
            # Buscar siguiente chunk secuencial
            sequential_successors = self.graph.get_successors(current, "sequential")
            
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
        
        for vertex_id in self.graph.graph_dict:
            sequential_predecessors = self.graph.get_predecessors(vertex_id, "sequential")
            if not sequential_predecessors:
                start_chunks.append(vertex_id)
        
        return start_chunks
    
    def get_contextual_chunks(self, chunk_id: str, context_radius: int = 2) -> Dict[str, Any]:
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
            'after': [],
            'metadata': self.graph.vertex_metadata.get(chunk_id, {})
        }
        
        # Obtener chunks anteriores siguiendo predecesores secuenciales
        current = chunk_id
        for _ in range(context_radius):
            predecessors = self.graph.get_predecessors(current, "sequential")
            if predecessors:
                prev_chunk = predecessors[0]  # Tomar el primer predecesor
                result['before'].insert(0, prev_chunk)
                current = prev_chunk
            else:
                break
        
        # Obtener chunks posteriores siguiendo sucesores secuenciales
        current = chunk_id
        for _ in range(context_radius):
            successors = self.graph.get_successors(current, "sequential")
            if successors:
                next_chunk = successors[0]['vertex']  # Tomar el primer sucesor
                result['after'].append(next_chunk)
                current = next_chunk
            else:
                break
        
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
        document_starts = self.find_document_start_chunks()
        
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
        document_path = self.reconstruct_document_path(start_chunk_id)
        
        # Enriquecer con metadatos
        enriched_chunks = []
        for i, chunk_id in enumerate(document_path):
            chunk_info = {
                'chunk_id': chunk_id,
                'position': i,
                'content': self.graph.vertex_metadata.get(chunk_id, {}).get('content', ''),
                'metadata': self.graph.vertex_metadata.get(chunk_id, {}),
                'is_start': i == 0,
                'is_end': i == len(document_path) - 1,
                'total_chunks': len(document_path)
            }
            enriched_chunks.append(chunk_info)
        
        return enriched_chunks
    
    def get_document_summary(self, document_id: str = None, start_chunk: str = None) -> Dict[str, Any]:
        """
        Obtener un resumen completo de un documento
        
        Args:
            document_id: ID del documento (si existe en document_structure)
            start_chunk: Chunk inicial para reconstruir el documento
            
        Returns:
            Diccionario con información completa del documento
        """
        if document_id and document_id in self.graph.document_structure:
            chunk_sequence = self.graph.document_structure[document_id]
            start_chunk = chunk_sequence[0] if chunk_sequence else None
        elif start_chunk:
            chunk_sequence = self.reconstruct_document_path(start_chunk)
        else:
            return {"error": "Debe proporcionar document_id o start_chunk"}
        
        if not chunk_sequence:
            return {"error": "No se pudo reconstruir el documento"}
        
        # Calcular estadísticas del documento
        total_chunks = len(chunk_sequence)
        total_content_length = 0
        chunk_details = []
        
        for i, chunk_id in enumerate(chunk_sequence):
            metadata = self.graph.vertex_metadata.get(chunk_id, {})
            content = metadata.get('content', '')
            content_length = len(content)
            total_content_length += content_length
            
            # Obtener conexiones del chunk
            successors = self.graph.get_successors(chunk_id)
            predecessors = self.graph.get_predecessors(chunk_id)
            
            chunk_detail = {
                'chunk_id': chunk_id,
                'position': i,
                'content_length': content_length,
                'content_preview': content[:100] + "..." if len(content) > 100 else content,
                'successors_count': len(successors),
                'predecessors_count': len(predecessors),
                'metadata': metadata
            }
            chunk_details.append(chunk_detail)
        
        summary = {
            'document_id': document_id,
            'start_chunk': chunk_sequence[0],
            'end_chunk': chunk_sequence[-1],
            'total_chunks': total_chunks,
            'total_content_length': total_content_length,
            'average_chunk_length': total_content_length / total_chunks if total_chunks > 0 else 0,
            'chunk_sequence': chunk_sequence,
            'chunk_details': chunk_details
        }
        
        return summary
    
    def navigate_document(self, current_chunk: str, direction: str = "next", steps: int = 1) -> Optional[str]:
        """
        Navegar por el documento desde un chunk actual
        
        Args:
            current_chunk: Chunk actual
            direction: "next", "previous", "start", "end"
            steps: Número de pasos a dar (para next/previous)
            
        Returns:
            ID del chunk de destino o None si no es posible
        """
        if direction == "start":
            # Ir al inicio del documento
            document_starts = self.find_document_start_chunks()
            # Buscar el inicio del documento actual
            temp_chunk = current_chunk
            while True:
                predecessors = self.graph.get_predecessors(temp_chunk, "sequential")
                if not predecessors:
                    return temp_chunk
                temp_chunk = predecessors[0]
        
        elif direction == "end":
            # Ir al final del documento
            document_path = self.reconstruct_document_path(current_chunk)
            return document_path[-1] if document_path else None
        
        elif direction == "next":
            # Avanzar hacia adelante
            current = current_chunk
            for _ in range(steps):
                successors = self.graph.get_successors(current, "sequential")
                if successors:
                    current = successors[0]['vertex']
                else:
                    break
            return current if current != current_chunk else None
        
        elif direction == "previous":
            # Retroceder
            current = current_chunk
            for _ in range(steps):
                predecessors = self.graph.get_predecessors(current, "sequential")
                if predecessors:
                    current = predecessors[0]
                else:
                    break
            return current if current != current_chunk else None
        
        return None
