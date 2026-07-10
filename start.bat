@echo off
title Ranjana Calligraphic AI Studio
echo ============================================
echo   Ranjana Calligraphic AI Studio - Windows
echo ============================================

REM Check if virtual environment exists
IF NOT EXIST ".venv\Scripts\python.exe" (
    echo [SETUP] Creating virtual environment...
    python -m venv .venv
    echo [SETUP] Installing dependencies...
    .venv\Scripts\pip install -r requirements.txt
    echo [SETUP] Done!
)

REM Kill anything already using port 8000
echo [INFO] Checking port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo [INFO] Killing process %%a on port 8000
    taskkill /PID %%a /F >nul 2>&1
)

echo [START] Launching server at http://localhost:8000
echo [INFO] Press Ctrl+C to stop.
echo.
.venv\Scripts\python.exe api.py
pause
