@echo off
REM GPA Simulator Launcher
REM Starts the Flask web application on http://127.0.0.1:5000

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10 or later from https://www.python.org/
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install -q flask werkzeug
)

REM Start the Flask app
echo.
echo ========================================
echo  GPA/CGPA Simulator
echo ========================================
echo.
echo Starting Flask development server...
echo Open your browser and navigate to:
echo   http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python ui_app.py

pause
