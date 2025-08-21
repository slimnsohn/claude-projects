@echo off
title Kalshi Quick Launch
cd /d "%~dp0"

REM Use system Python first (better SSL support)
python --version >nul 2>&1
if errorlevel 1 (
    if exist "C:\Users\sammy\anaconda3\python.exe" (
        set PYTHON_CMD=C:\Users\sammy\anaconda3\python.exe
    ) else (
        set PYTHON_CMD=python
    )
) else (
    set PYTHON_CMD=python
)

echo Starting Kalshi Dashboard...
echo Open your browser to http://localhost:8000
echo.

REM Start the server and open browser after a short delay
start /min timeout 3 >nul && start "" http://localhost:8000
%PYTHON_CMD% serve_dashboard.py 8000

pause