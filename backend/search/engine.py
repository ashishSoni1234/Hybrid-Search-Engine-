import os
import json
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def min_max_normalize(scores):
    if len(scores) == 0:
        return scores
    min_val = np.min(scores)
    max_val = np.max(scores)
    if max_val - min_val == 0:
        return np.ones_like(scores)
    return (scores - min_val) / (max_val - min_val)

def z_score_normalize(scores):
    if len(scores) == 0:
        return scores
    mean = np.mean(scores)
    std = np.std(scores)
    if std == 0:
        return np.zeros_like(scores)
    return (scores - mean) / std

class HybridSearchEngine:
    def __init__(self):
        self.bm25 = None
        self.docs = None
        self.doc_ids = None
        self.vector_index = None
        self.model = None
        self.is_ready = False
        self.load_indexes()
        
    def load_indexes(self):
        bm25_path = os.path.join("data", "index", "bm25", "index.pkl")
        vector_path = os.path.join("data", "index", "vector", "index.faiss")
        metadata_path = os.path.join("data", "index", "vector", "metadata.json")
        
        if os.path.exists(bm25_path):
            with open(bm25_path, "rb") as f:
                data = pickle.load(f)
                self.bm25 = data["bm25"]
                self.docs = data["docs"]
                self.doc_ids = data["doc_ids"]
                
        if os.path.exists(vector_path) and os.path.exists(metadata_path):
            self.vector_index = faiss.read_index(vector_path)
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                model_name = metadata.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
                self.model = SentenceTransformer(model_name)
                
        if self.bm25 and self.vector_index:
            self.is_ready = True
    
    def search(self, query: str, top_k: int = 10, alpha: float = 0.5, norm_strategy: str = "min-max"):
        if not self.is_ready:
            return []
            
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")
        
        D, I = self.vector_index.search(query_embedding, len(self.docs))
        
        vector_scores = np.zeros(len(self.docs))
        for i, doc_idx in enumerate(I[0]):
            vector_scores[doc_idx] = 1.0 / (1.0 + D[0][i])
            
        if norm_strategy == "min-max":
            norm_bm25 = min_max_normalize(bm25_scores)
            norm_vector = min_max_normalize(vector_scores)
        else:
            norm_bm25 = z_score_normalize(bm25_scores)
            norm_vector = z_score_normalize(vector_scores)
            
        hybrid_scores = alpha * norm_bm25 + (1 - alpha) * norm_vector
        
        if len(hybrid_scores) == 0:
            return []
            
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            doc = self.docs[idx]
            snippet = doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"]
            results.append({
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "bm25_score": float(bm25_scores[idx]),
                "vector_score": float(vector_scores[idx]),
                "hybrid_score": float(hybrid_scores[idx]),
                "snippet": snippet
            })
            
        return results
