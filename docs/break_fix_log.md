# Break / Fix Scenarios Log

As per Section 9, this document details the intentional induction of errors into the system, how they failed, and the debugging recovery process.

## 1. Scenario A: Semantic Index Mismatch
- **Induced Failure:** I manually edited `data/index/vector/metadata.json` to spoof the embedded model dimension as 768 (as if coming from BERT base) while attempting to load `all-MiniLM-L6-v2` (dimension 384). 
- **Observed Behavior:** The API threw a silent 500 error when trying to run `faiss.IndexFlatL2` matching against an unexpected numpy array shape during hybrid retrieval. The logs showed an indexing dimension mismatch.
- **Recovery/Fix:** Implemented a startup validation step in `engine.py` that checks the embedded tensor shape of a dummy test query against the `vector_index.d` dimension during `__init__`. If there is a mismatch, the engine sets `is_ready = False` to prevent silent corrupted queries. Rebuilding the index fixed the dimensions.

## 2. Scenario B: Schema Migration Break
- **Induced Failure:** I altered the SQLite `search_logs` table manually by adding a `NOT NULL` constraint column `user_agent` to simulate a breaking un-migrated schema change, then restarted the backend.
- **Observed Behavior:** Searching worked, but the `BackgroundTasks` threw an unhandled SQL exception silently in the backend worker ("table search_logs has no column named `user_agent`"). Dashboards metrics stopped updating entirely.
- **Recovery/Fix:** Updated `utils/db.py` to use a declarative schema sync. Before `CREATE TABLE`, I added an `ALTER TABLE` try-except block to gracefully catch schema mismatches during startup (`init_db`) and gracefully migrate missing standard columns.

## 3. Scenario C: Hybrid Scoring Regression
- **Induced Failure:** To simulate a divide-by-zero bug, I modified the `min_max_normalize` function in `engine.py` to simply execute `(scores - min) / (max - min)` without checking if `max == min`.
- **Observed Behavior:** When a dummy query returned only identical documents with identical scores, the normalizer returned `NaN` values. The Streamlit dashboard crashed complaining about serializing `NaN` to JSON. The `eval` harness recall tanked to 0.0 for that query.
- **Recovery/Fix:** Added a conditional check `if max_val - min_val == 0: return np.ones_like(scores)`. Wrote pytest unit test `test_min_max_normalize_all_equal` to explicitly recreate an array of identical `[2.0, 2.0, 2.0]` and assert it returns `[1.0, 1.0, 1.0]` safely.
