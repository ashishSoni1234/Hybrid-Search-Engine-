$ErrorActionPreference = "Stop"

Write-Host "==========================================="
Write-Host " Hybrid Knowledge Search - Setup (Windows) "
Write-Host "==========================================="

# 1) Create virtual environment
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}
else {
    Write-Host "Virtual environment already exists."
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Set PYTHONPATH so -m module imports work
$env:PYTHONPATH = (Get-Location).Path

# 2) Install / upgrade dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt --quiet

# 3) Download dataset if missing or empty
$docsPath = "data\processed\docs.jsonl"
$docsExists = (Test-Path $docsPath) -and ((Get-Item $docsPath).length -gt 0)

if (-Not $docsExists) {
    Write-Host "Fetching Wikipedia summaries (~400 documents)..."
    python -m backend.ingest --input data\raw --out data\processed
}
else {
    Write-Host "Dataset already present."
}

# 4) Build indexes if missing
$bm25Exists = Test-Path "data\index\bm25\index.pkl"
$faissExists = Test-Path "data\index\vector\index.faiss"

if (-Not ($bm25Exists -and $faissExists)) {
    Write-Host "Building BM25 and Vector indexes..."
    python -m backend.index --input data\processed\docs.jsonl
}
else {
    Write-Host "Indexes already exist."
}

# 5) Run tests
Write-Host "Running pytest..."
python -m pytest tests\ -v

# 6) Run evaluation
Write-Host "Running evaluation experiments..."
python -m backend.eval --queries data\eval\queries.jsonl --qrels data\eval\qrels.json

Write-Host ""
Write-Host "==========================================="
Write-Host " Starting Services...                      "
Write-Host "==========================================="

# Start FastAPI in a new window
Write-Host "Starting FastAPI server on port 8000..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$((Get-Location).Path)'; `$env:PYTHONPATH='$((Get-Location).Path)'; .\venv\Scripts\Activate.ps1; uvicorn backend.api.main:app --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

# Start Streamlit in a new window
Write-Host "Starting Streamlit dashboard on port 8501..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$((Get-Location).Path)'; `$env:PYTHONPATH='$((Get-Location).Path)'; .\venv\Scripts\Activate.ps1; streamlit run frontend\dashboard.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"

Write-Host ""
Write-Host "==========================================="
Write-Host " System is UP!                             "
Write-Host "==========================================="
Write-Host ""
Write-Host " FastAPI Backend:  http://localhost:8000"
Write-Host " API Swagger Docs: http://localhost:8000/docs"
Write-Host " Streamlit App:    http://localhost:8501"
Write-Host ""
Write-Host "Two new terminal windows have been opened."
Write-Host "Close them to stop the servers."
Write-Host "==========================================="
