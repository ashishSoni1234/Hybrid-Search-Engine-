# Decision Log
- Decided to use Wikipedia API sequentially with `tqdm` to avoid overwhelming rate limits while easily expanding documents based on related titles.
- Chose `SQLite` for local latency metric tracking and observability logs since it's easy to spin up and fits within the "CPU only" and "single machine" footprint constraint.
- Went with standard `BM25Okapi` mapping tokens linearly and normalizing min-max or z-scores dynamically across query results to handle out-of-scale variations with FAISS L2 distances.
