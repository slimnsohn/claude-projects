@echo off
echo Testing Python detection...

python --version >nul 2>&1
if errorlevel 1 (
    echo System Python not found
    if exist "C:\Users\sammy\anaconda3\python.exe" (
        echo Using Anaconda Python
        set PYTHON_CMD=C:\Users\sammy\anaconda3\python.exe
    ) else (
        echo No Python found
        exit /b 1
    )
) else (
    echo System Python found!
    set PYTHON_CMD=python
)

echo Python command: %PYTHON_CMD%
%PYTHON_CMD% --version
echo Test complete!
pause