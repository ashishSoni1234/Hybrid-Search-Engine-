import sqlite3
import os
import json
import logging
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join("data", "metrics", "observability.db")
LOG_PATH = os.path.join("data", "metrics", "app_logs.jsonl")

logger = logging.getLogger("hybrid_search")
logger.setLevel(logging.INFO)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
fh = logging.FileHandler(LOG_PATH)
logger.addHandler(fh)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_logs (
                request_id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                top_k INTEGER NOT NULL,
                alpha REAL NOT NULL,
                result_count INTEGER NOT NULL,
                error TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

@contextmanager
def get_db_cursor():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn.cursor()
    finally:
        conn.commit()
        conn.close()

def log_search(request_id: str, query: str, latency_ms: float, top_k: int, alpha: float, result_count: int, error: str = ""):
    # 1. Persist to SQLite
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO search_logs (request_id, query, latency_ms, top_k, alpha, result_count, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (request_id, query, latency_ms, top_k, alpha, result_count, error))
        
    # 2. Structured JSON Log
    log_record = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "query": query,
        "latency_ms": latency_ms,
        "top_k": top_k,
        "alpha": alpha,
        "result_count": result_count,
        "error": error,
        "severity": "ERROR" if error else "INFO"
    }
    logger.info(json.dumps(log_record))
