@echo off
title Kalshi Trading Dashboard
echo =====================================
echo   Kalshi Trading Dashboard Launcher
echo =====================================
echo.
echo Starting dashboard server...
echo.
echo Dashboard will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server when you're done
echo.

REM Change to the directory where the batch file is located
cd /d "%~dp0"

REM Check if Anaconda Python is available first
if exist "C:\Users\sammy\anaconda3\python.exe" (
    echo Using Anaconda Python...
    set PYTHON_CMD=C:\Users\sammy\anaconda3\python.exe
) else (
    REM Fallback to system Python
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python and try again.
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
)

REM Start the dashboard server
echo Starting server...
%PYTHON_CMD% serve_dashboard.py

REM If the server stops, pause so user can see any error messages
echo.
echo Server stopped.
pause