@echo off
title NEXUS AI - Streamlit Cyber Frontend (Port 8501)
cd /d "%~dp0frontend"

echo ===================================================
echo   Starting NEXUS AI Streamlit Cyber UI Frontend
echo ===================================================

if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
)

python -m streamlit run app.py
pause
