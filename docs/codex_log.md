# Codex Usage Protocol & Prompt Log

This document records the incremental use of Codex/LLM for this assignment, ensuring that blanket prompts were not used and every step was auditable and maps to a testable unit of work.

## Sequence 1: Data Ingestion
- **Prompt:** "In `backend/ingest/__main__.py`, write a python script using `requests` and `tqdm` to fetch Wikipedia summaries for computational topics. Include a bounded error handler to avoid crashing on Bad HTTP responses. Normalize the whitespace."
- **Edits made:** I manually added `datetime.utcnow().isoformat()` missing from the AI output and handled `requests.exceptions.Timeout` explicitly before committing.
- **Commit:** `feat: Create data ingestion pipeline for Wikipedia summaries`

## Sequence 2: Indexing Pipeline
- **Prompt:** "In `backend/index/__main__.py`, create a script that reads the ingested JSONL file and builds a `rank-bm25` BM25Okapi index and a FAISS L2 index using `sentence-transformers/all-MiniLM-L6-v2`. Save the models via pickle and faiss."
- **Edits made:** I had to fix the FAISS array typing (`astype('float32')`) because the AI used float64 which faiss-cpu rejected.
- **Commit:** `feat: Build lexical and semantic indexing artifacts`

## Sequence 3: FastAPI Search Engine
- **Prompt:** "In `backend/search/engine.py` and `backend/api/main.py`, implement an asynchronous FastAPI wrapper around the Hybrid Search Engine. The search engine needs to implement min-max normalization merging dense vectors and reciprocal BM25 scores."
- **Edits made:** The AI used a synchronous SQLite connection which blocked I/O. I rewrote the metric insertion via FastAPI `BackgroundTasks` to preserve low latency.
- **Commit:** `feat: FastAPI search endpoint with background task logging`

## Sequence 4: Streamlit Dashboard
- **Prompt:** "In `frontend/dashboard.py`, create a Streamlit multipage dashboard using Python. Include a Search tab with an alpha slider, a KPI page for metrics retrieved from SQLite, and a Logs tab."
- **Edits made:** I added missing timezone normalizations using `pd.to_datetime` and the UI filters for Time Range and Severity that weren't generated correctly by the LLM.
- **Commit:** `feat: Streamlit dashboard with KPI charts and search interface`
