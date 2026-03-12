# Hybrid Knowledge Search + KPI Dashboard

A small end-to-end product that demonstrates hybrid lexical-semantic searching with an emphasis on production architecture, search relevancy, and real-time observability.

## Architecture Overview

The system runs entirely on CPU:
- **Lexical Search**: `rank-bm25`
- **Dense Vector Search**: `faiss-cpu` combined with `sentence-transformers/all-MiniLM-L6-v2`
- **Backend**: FastAPI + Uvicorn
- **Metrics/Logging**: SQLite local file tracking
- **Frontend**: Streamlit multi-page dashboard.

## 1-Minute Quickstart

Run the following command to completely set up and run the system. This handles virtual environments, data ingest (if missing), indexing, and booting the servers.

```bash
./up.sh
```

*(On Windows, run from Bash or execute `./up.ps1` if converted, but standard Shell/Bash emulators like Git Bash can run `./up.sh` directly)*

Then visit `http://localhost:8501` to use the Streamlit Dashboard.

## How to Run Search

Once the servers are running, access the dashboard and use the **Search** page. 

You can also use the API directly:
```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "machine learning", "top_k": 5, "alpha": 0.5}'
```

## How to Run Evaluation

The project includes an evaluation harness measuring MRR, Recall, and nDCG across alpha configurations (0.0 to 1.0).

Activate your virtual environment and run:
```bash
python -m backend.eval --queries data/eval/queries.jsonl --qrels data/eval/qrels.json
```
Results are saved to `data/metrics/experiments.csv`.

## How to Run Tests

Pytest suite runs against the mathematical bounds of our normalizers and endpoint sanity checks.

Activate your virtual environment and run:
```bash
pytest tests/
```
