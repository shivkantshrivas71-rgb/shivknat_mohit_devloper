@echo off
title NEXUS AI - FastAPI Backend API Server (Port 8000)
cd /d "%~dp0backend"

echo ===================================================
echo   Starting NEXUS AI FastAPI Backend API Server
echo ===================================================

if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
)

python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
