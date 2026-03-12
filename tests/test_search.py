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
