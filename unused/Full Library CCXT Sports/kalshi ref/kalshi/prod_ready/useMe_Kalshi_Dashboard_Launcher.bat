@echo off
setlocal enabledelayedexpansion
title Kalshi Trading Dashboard - Robust Launcher
color 0A

echo =========================================================
echo   Kalshi Trading Dashboard - Robust Launcher
echo =========================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Verify we're in the right location
if not exist "serve_dashboard.py" (
    echo ERROR: serve_dashboard.py not found in current directory
    echo Current directory: %CD%
    echo Please make sure you're running this from the prod_ready folder
    pause
    exit /b 1
)

REM Check for Python installations (prefer system Python for SSL)
set PYTHON_CMD=

echo [*] Checking for system Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] System Python not found, checking Anaconda...
    if exist "C:\Users\sammy\anaconda3\python.exe" (
        echo [!] Using Anaconda Python ^(may have SSL issues^)
        set PYTHON_CMD=C:\Users\sammy\anaconda3\python.exe
    ) else (
        echo [✗] ERROR: No Python installation found
        echo Please install Python and try again
        pause
        exit /b 1
    )
) else (
    echo [✓] Found system Python ^(preferred for SSL^)
    set PYTHON_CMD=python
)

REM Test Python and required modules
echo [*] Testing Python environment...
%PYTHON_CMD% -c "import http.server, socketserver, json; print('[✓] Core modules available')" 2>nul
if errorlevel 1 (
    echo [✗] ERROR: Python environment test failed
    pause
    exit /b 1
)

REM Find available port
echo [*] Finding available port...
set PORT=8000
:find_port
netstat -an | findstr ":%PORT% " >nul 2>&1
if not errorlevel 1 (
    set /a PORT+=1
    if !PORT! gtr 8020 (
        echo [✗] ERROR: No available ports found between 8000-8020
        pause
        exit /b 1
    )
    goto find_port
)

echo [✓] Using port: !PORT!
echo.
echo =========================================================
echo   Dashboard will be available at:
echo   http://localhost:!PORT!
echo =========================================================
echo.
echo [*] Starting server... (Press Ctrl+C to stop)
echo.

REM Start server with error handling
%PYTHON_CMD% serve_dashboard.py !PORT!
set exit_code=%errorlevel%

echo.
echo =========================================================
if %exit_code% equ 0 (
    echo   Server stopped normally
) else (
    echo   Server stopped with error code: %exit_code%
    echo   Check the error messages above for details
)
echo =========================================================
echo.
echo Press any key to close this window...
pause >nul