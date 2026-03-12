import argparse
import os
import json
import pandas as pd
import numpy as np
from collections import defaultdict
import subprocess
from datetime import datetime
from backend.search.engine import HybridSearchEngine

def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip()
    except Exception:
        return "unknown"

def calculate_mrr(rankings, qrels):
    mrr = 0.0
    for qid, results in rankings.items():
        relevant_docs = qrels.get(qid, set())
        for rank, doc_id in enumerate(results, 1):
            if doc_id in relevant_docs:
                mrr += 1.0 / rank
                break
    return mrr / len(rankings) if rankings else 0.0

def calculate_recall_at_k(rankings, qrels, k=10):
    recall = 0.0
    for qid, results in rankings.items():
        relevant_docs = qrels.get(qid, set())
        if not relevant_docs:
            continue
        hits = sum(1 for doc_id in results[:k] if doc_id in relevant_docs)
        recall += hits / len(relevant_docs)
    return recall / len(rankings) if rankings else 0.0

def calculate_ndcg_at_k(rankings, qrels, k=10):
    ndcg = 0.0
    for qid, results in rankings.items():
        relevant_docs = qrels.get(qid, set())
        if not relevant_docs:
            continue
            
        dcg = 0.0
        for rank, doc_id in enumerate(results[:k], 1):
            if doc_id in relevant_docs:
                dcg += 1.0 / np.log2(rank + 1)
                
        idcg = sum(1.0 / np.log2(rank + 1) for rank in range(1, min(k, len(relevant_docs)) + 1))
        
        if idcg > 0:
            ndcg += dcg / idcg
            
    return ndcg / len(rankings) if rankings else 0.0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=str, required=True, help="Queries JSONL file")
    parser.add_argument("--qrels", type=str, required=True, help="Qrels JSON file")
    args = parser.parse_args()

    # Load queries
    queries = []
    with open(args.queries, "r") as f:
        for line in f:
            if line.strip():
                queries.append(json.loads(line))

    # Load qrels format: {"q_id": [doc_id1, doc_id2, ...]}
    with open(args.qrels, "r") as f:
         qrels_raw = json.load(f)
         qrels = {k: set(v) for k, v in qrels_raw.items()}

    engine = HybridSearchEngine()
    
    experiments = []
    alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    print(f"Running evaluation with {len(queries)} queries...")
    
    for alpha in alphas:
        rankings = defaultdict(list)
        
        for query_data in queries:
            qid = query_data["q_id"]
            query_text = query_data["query"]
            results = engine.search(query_text, top_k=10, alpha=alpha)
            rankings[qid] = [r["doc_id"] for r in results]
            
        mrr = calculate_mrr(rankings, qrels)
        recall = calculate_recall_at_k(rankings, qrels, k=10)
        ndcg = calculate_ndcg_at_k(rankings, qrels, k=10)
        
        print(f"Alpha {alpha:0.2f} -> MRR@10: {mrr:.4f}, Recall@10: {recall:.4f}, nDCG@10: {ndcg:.4f}")
        
        experiments.append({
            "timestamp": datetime.utcnow().isoformat(),
            "git_commit": get_git_commit(),
            "alpha": alpha,
            "mrr_at_10": mrr,
            "recall_at_10": recall,
            "ndcg_at_10": ndcg
        })
        
    df = pd.DataFrame(experiments)
    
    filepath = "data/metrics/experiments.csv"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if os.path.exists(filepath):
        df.to_csv(filepath, mode='a', header=False, index=False)
    else:
        df.to_csv(filepath, index=False)
    print("Evaluation results appended to data/metrics/experiments.csv")

if __name__ == "__main__":
    main()
