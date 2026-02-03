@echo off
REM Local Lode - Unified Launcher
REM Single-click launcher for Local Lode application

echo ============================================================
echo   Local Lode - Note Search Tool
echo ============================================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python.
)

echo.
echo Starting Local Lode...
echo.

REM Run the Python launcher
python launcher_new.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
