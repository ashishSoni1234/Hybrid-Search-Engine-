# Implementation Notes

- Designed to be completely self-contained over CPU bounds via pure `sentence-transformers` models (`all-MiniLM-L6-v2`) processing natively via FAISS CPU index.
- FastAPI backend routes query metrics and latency data asynchronously via background task into local SQLite for real-time observability mapping inside the dashboard.
