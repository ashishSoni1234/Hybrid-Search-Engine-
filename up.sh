#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "==========================================="
echo " Starting Hybrid Knowledge Search Setup... "
echo "==========================================="

# 1) Detect Python command and create virtual environment
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "Error: Python 3 is not installed or not in PATH."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment using $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
# Windows Git Bash compatibility
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Set PYTHONPATH so python -m module commands work
export PYTHONPATH="."

# 2) Install dependencies
echo "Installing dependencies..."
python -m pip install -r requirements.txt

# 3) Download dataset if missing
if [ ! -f "data/processed/docs.jsonl" ]; then
    echo "Dataset mostly missing. Fetching Wikipedia summaries (~400 documents)..."
    python -m backend.ingest --input data/raw --out data/processed
else
    echo "Dataset already present at data/processed/docs.jsonl."
fi

# 4) Build indexes if missing
if [ ! -f "data/index/bm25/index.pkl" ] || [ ! -f "data/index/vector/index.faiss" ]; then
    echo "Indexes missing. Building BM25 and Vector indexes..."
    python -m backend.index --input data/processed/docs.jsonl
else
    echo "Indexes already exist."
fi

echo "Running tests..."
$PYTHON_CMD -m pytest tests/

echo "Running eval (generating experiments.csv)..."
$PYTHON_CMD -m backend.eval --queries data/eval/queries.jsonl --qrels data/eval/qrels.json

echo "==========================================="
echo " Starting Services...                      "
echo "==========================================="

# Kill running processes on these ports if any (useful for restarts)
# This part is somewhat OS dependent, kept simple for standard unix-like

# Setup trap to catch CTRL+C and cleanly kill background processes
cleanup() {
    echo "Stopping background services..."
    kill $FASTAPI_PID $STREAMLIT_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 5) Start FastAPI server in background
echo "Starting FastAPI server on port 8000..."
$PYTHON_CMD -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 &
FASTAPI_PID=$!

# Wait a moment for the server to start
sleep 3

# 6) Start Streamlit dashboard in background
echo "Starting Streamlit dashboard..."
$PYTHON_CMD -m streamlit run frontend/dashboard.py --server.port 8501 --server.address 127.0.0.1 --server.headless true &
STREAMLIT_PID=$!

# 7) Print URLs
echo ""
echo "==========================================="
echo " System is UP and RUNNING!                 "
echo "==========================================="
echo ""
echo " -> FastAPI Backend:   http://127.0.0.1:8000"
echo " -> API Docs:          http://127.0.0.1:8000/docs"
echo " -> Streamlit App:     http://127.0.0.1:8501"
echo ""
echo "Press Ctrl+C to stop all services."
echo "==========================================="

# Wait for both background processes
wait $FASTAPI_PID $STREAMLIT_PID
