from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import time
import uuid
import sqlite3
import os

from backend.search.engine import HybridSearchEngine
from backend.utils.db import init_db, log_search

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (nothing to clean up)

app = FastAPI(title="Hybrid Knowledge Search API", version="1.0.0", lifespan=lifespan)

search_engine = HybridSearchEngine()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    alpha: float = 0.5
    norm_strategy: str = "min-max"


class FeedbackRequest(BaseModel):
    request_id: str
    doc_id: int
    relevance: int


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "commit_hash": "placeholder"
    }


@app.post("/search")
async def search(req: SearchRequest, background_tasks: BackgroundTasks):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        results = search_engine.search(
            query=req.query,
            top_k=req.top_k,
            alpha=req.alpha,
            norm_strategy=req.norm_strategy
        )
        latency_ms = (time.time() - start_time) * 1000

        background_tasks.add_task(
            log_search,
            request_id=request_id,
            query=req.query,
            latency_ms=latency_ms,
            top_k=req.top_k,
            alpha=req.alpha,
            result_count=len(results),
            error=""
        )

        return {
            "request_id": request_id,
            "results": results,
            "latency_ms": latency_ms
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        background_tasks.add_task(
            log_search,
            request_id=request_id,
            query=req.query,
            latency_ms=latency_ms,
            top_k=req.top_k,
            alpha=req.alpha,
            result_count=0,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
def feedback(req: FeedbackRequest):
    return {"status": "recorded", "request_id": req.request_id}


@app.get("/metrics")
def metrics():
    db_path = os.path.join("data", "metrics", "observability.db")
    if not os.path.exists(db_path):
        return {"total_queries": 0, "avg_latency_ms": 0.0}

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM search_logs")
        total_queries = cur.fetchone()[0]

        cur.execute("SELECT AVG(latency_ms) FROM search_logs")
        avg_latency = cur.fetchone()[0] or 0.0

    return {
        "total_queries": total_queries,
        "avg_latency_ms": avg_latency
    }
