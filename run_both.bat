@echo off
title NEXUS AI - Launcher
cd /d "%~dp0"

echo ===================================================
echo   Launching NEXUS AI (Backend + Frontend)
echo ===================================================

start "NEXUS AI Backend" cmd /k "run_backend.bat"
timeout /t 3 /nobreak >nul
start "NEXUS AI Frontend" cmd /k "run_frontend.bat"

echo Both Backend (Port 8000) and Frontend (Port 8501) launched!
