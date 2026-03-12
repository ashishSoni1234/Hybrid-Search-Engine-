# Architecture

## Overview
The Hybrid Knowledge Search + KPI Dashboard system is composed of several key modules:
- **Ingestion Pipeline (`backend/ingest`)**: Scrapes data from the Wikipedia API to create a dataset of ~400 documents.
- **Indexing (`backend/index`)**: Constructs a lexical index using `rank-bm25` and a dense vector index using `FAISS` (CPU) and `sentence-transformers`.
- **Search Engine (`backend/search`)**: In-memory module that blends scores using a dynamic `alpha` parameter for hybrid lexical-semantic retrieval.
- **REST API (`backend/api`)**: A FastAPI application that provides search functionality and integrates with SQLite for basic observability.
- **Evaluation Harness (`backend/eval`)**: A module for calculating MRR, nDCG, and Recall for a set of queries.
- **Dashboard (`frontend`)**: A Streamlit application rendering search UI and insights from observability logs.

## Stack
- **Python 3.11**
- **FastAPI / Uvicorn** for Backend API
- **Rank-BM25 & FAISS CPU & Sentence Transformers** for Search backend.
- **SQLite** for Metrics / Storage.
- **Streamlit** for Frontend UI.
- **Pytest** for testing.
