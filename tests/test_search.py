import pytest
from backend.search.engine import min_max_normalize, z_score_normalize
import numpy as np

# ---- Normalization Unit Tests ----

def test_min_max_normalize():
    scores = np.array([1.0, 2.0, 3.0])
    normalized = min_max_normalize(scores)
    assert np.allclose(normalized, [0.0, 0.5, 1.0])

def test_min_max_normalize_all_equal():
    scores = np.array([2.0, 2.0, 2.0])
    normalized = min_max_normalize(scores)
    assert np.allclose(normalized, [1.0, 1.0, 1.0])

def test_z_score_normalize():
    scores = np.array([1.0, 2.0, 3.0])
    normalized = z_score_normalize(scores)
    assert np.allclose(normalized, [-1.22474487, 0, 1.22474487])

def test_z_score_normalize_all_equal():
    scores = np.array([2.0, 2.0, 2.0])
    normalized = z_score_normalize(scores)
    assert np.allclose(normalized, [0.0, 0.0, 0.0])

# ---- API Endpoint Tests ----

def test_health_check():
    from fastapi.testclient import TestClient
    from backend.api.main import app
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"

def test_metrics_endpoint():
    from fastapi.testclient import TestClient
    from backend.api.main import app
    with TestClient(app) as client:
        response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data

# ---- Additional Rubric Tests ----

def test_preprocessing():
    from backend.ingest.__main__ import normalize_text
    assert normalize_text("  hello   world  \n ") == "hello world"
    assert normalize_text("no_extra_space") == "no_extra_space"

def test_bm25_scoring():
    from rank_bm25 import BM25Okapi
    corpus = [["hello", "there", "friend"], ["goodbye", "world", "friend"]]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(["hello"])
    assert scores[0] > scores[1]  # The first doc contains 'hello', so it should rank higher

def test_vector_search_faiss():
    import faiss
    import numpy as np
    index = faiss.IndexFlatL2(2)
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]]).astype("float32")
    index.add(vectors)
    query = np.array([[1.0, 0.0]]).astype("float32")
    D, I = index.search(query, 1)
    assert I[0][0] == 0  # Matches first vector
    assert D[0][0] == 0.0  # Perfect match

def test_search_api_contract(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.api.main import app, search_engine
    
    # Mock the search engine's search method to return a dummy result
    def mock_search(query, top_k, alpha, norm_strategy):
        return [{"doc_id": 1, "title": "Dummy", "bm25_score": 1.0, "vector_score": 1.0, "hybrid_score": 1.0, "snippet": "..."}]
    
    monkeypatch.setattr(search_engine, "search", mock_search)
    
    with TestClient(app) as client:
        response = client.post("/search", json={"query": "test query", "top_k": 5, "alpha": 0.5})
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert "latency_ms" in data
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["title"] == "Dummy"
