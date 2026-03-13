#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "==========================================="
echo " Stopping Hybrid Knowledge Search...       "
echo "==========================================="

# Find and kill FastAPI (uvicorn)
if pgrep -f "uvicorn backend.api.main:app" > /dev/null; then
    echo "Stopping FastAPI server..."
    pkill -f "uvicorn backend.api.main:app"
else
    echo "FastAPI server is not running."
fi

# Find and kill Streamlit
if pgrep -f "streamlit run frontend/dashboard.py" > /dev/null; then
    echo "Stopping Streamlit dashboard..."
    pkill -f "streamlit run frontend/dashboard.py"
else
    echo "Streamlit dashboard is not running."
fi

echo "==========================================="
echo " Services stopped cleanly!                 "
echo "==========================================="
