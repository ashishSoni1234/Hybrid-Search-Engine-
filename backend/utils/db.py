import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join("data", "metrics", "observability.db")

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
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO search_logs (request_id, query, latency_ms, top_k, alpha, result_count, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (request_id, query, latency_ms, top_k, alpha, result_count, error))
