import faiss
import numpy as np

class RootFinder:
    def __init__(self, data):
        self.document_tree= {}
        self.doc_ids= []
        self.embeddings= []
        self.index= None

    def add_document(self, doc_id, embedding):
        self.document_tree[doc_id] = embedding
        self.doc_ids.append(doc_id)
        root_embedding = self._get_root_embedding(graph.root)
        self.embeddings.append(root_embedding)

    def build_index(self):
        embeddings_array = np.array(self.embeddings).astype('float32')
        dimension = embeddings_array.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_array)
        print(f"Index built with {self.index.ntotal} vectors.")

    def find_relevant_roots(self, query, k=5):
        query_embedding = self.encode_query(query).astype('float32')
        scores, indices = self.index.search(query_embedding.reshape(1, -1), k)
    
        relevantes_roots = []
        for idx in indices[0]:
            if idx < len(self.doc_ids):
                relevantes_roots.append(self.doc_ids[idx])
        return relevantes_roots

    def search(self, query, k=5):
        relevant_roots = self.find_relevant_roots(query, k)
        all_results = []
        for root in relevant_roots:
            results = self.document_tree[root].search(query, k)
            all_results.extend(results)
        all_results.sort(key=lambda x: x[1], reverse=True)
        
            for result in tree_results:
                combined_score= rppt_scroer * 0.7 + tree_score * 0.3
                all_results.append((node, combined_score))
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results[:k]    