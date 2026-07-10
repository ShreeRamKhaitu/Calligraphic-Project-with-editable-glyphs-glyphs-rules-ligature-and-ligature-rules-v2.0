#!/bin/bash
echo "============================================"
echo "  Ranjana Calligraphic AI Studio - Linux"
echo "============================================"

# Check if virtual environment exists
if [ ! -f ".venv/bin/python3" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv .venv
    echo "[SETUP] Installing dependencies..."
    .venv/bin/pip install -r requirements.txt
    echo "[SETUP] Done!"
fi

# Kill anything already using port 8000
echo "[INFO] Checking port 8000..."
if command -v fuser &> /dev/null; then
    fuser -k 8000/tcp 2>/dev/null && echo "[INFO] Cleared port 8000."
else
    PID=$(lsof -ti:8000 2>/dev/null)
    if [ -n "$PID" ]; then
        kill -9 $PID 2>/dev/null && echo "[INFO] Cleared port 8000."
    fi
fi

echo "[START] Launching server at http://localhost:8000"
echo "[INFO] Press Ctrl+C to stop."
echo ""
.venv/bin/python3 api.py
