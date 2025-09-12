# Arquitectura limpia y simple
class TreeGraphRAG:
    def __init__(self):
        self.trees = {}  # {doc_id: TreeGraph}
        self.root_index = faiss.IndexFlatIP(768)  # Solo raíces
        
    def search(self, query, k=5):
        # 1. FAISS: encontrar top-k raíces (ultra rápido)
        query_emb = self.encode(query)
        scores, doc_indices = self.root_index.search(query_emb, k)
        
        # 2. Buscar solo en esos k árboles específicos
        results = []
        for i, doc_idx in enumerate(doc_indices[0]):
            doc_id = self.doc_ids[doc_idx]
            tree_results = self.search_in_tree(self.trees[doc_id], query)
            results.extend([(r, scores[0][i]) for r in tree_results])
        
        return results