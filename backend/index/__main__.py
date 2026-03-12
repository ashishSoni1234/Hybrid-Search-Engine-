import argparse
import os
import json
import pickle
import numpy as np
import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import hashlib

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input raw JSONL file")
    args = parser.parse_args()

    docs = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))
                
    if not docs:
        print("No documents found in the provided input file.")
        return

    print("Building indexes for", len(docs), "documents...")
    texts = [doc["text"] for doc in docs]
    doc_ids = [doc["doc_id"] for doc in docs]
    
    print("Building BM25 index...")
    tokenized_texts = [text.lower().split() for text in texts]
    bm25 = BM25Okapi(tokenized_texts)
    
    os.makedirs(os.path.join("data", "index", "bm25"), exist_ok=True)
    with open(os.path.join("data", "index", "bm25", "index.pkl"), "wb") as f:
        pickle.dump({"bm25": bm25, "doc_ids": doc_ids, "docs": docs}, f)

    print("Building Vector index...")
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")
    
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    
    os.makedirs(os.path.join("data", "index", "vector"), exist_ok=True)
    faiss.write_index(index, os.path.join("data", "index", "vector", "index.faiss"))
    
    with open(os.path.join("data", "index", "vector", "metadata.json"), "w") as f:
        corpus_hash = hashlib.md5("".join(texts).encode("utf-8")).hexdigest()
        metadata = {
            "embedding_model": model_name,
            "embedding_dimension": dim,
            "corpus_hash": corpus_hash,
            "num_docs": len(docs)
        }
        json.dump(metadata, f, indent=4)
        
    print("Indexing complete.")

if __name__ == "__main__":
    main()
