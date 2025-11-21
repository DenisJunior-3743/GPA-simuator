@echo off
REM CLI launcher for GPA Simulator (works with packaged exe and source)
REM When packaged: This script should be in the distribution folder alongside the exe
REM When in source: This script is in the project root

setlocal enabledelayedexpansion

REM Get the current script directory
set "SCRIPT_DIR=%~dp0"

REM Check if we're in a packaged environment (look for gpa_simulator.exe in same directory)
if exist "!SCRIPT_DIR!gpa_simulator.exe" (
    echo.
    echo Launching GPA Simulator CLI...
    echo.
    REM When packaged, main.py should be accessible via Python path or we need to find it
    REM The packaged exe has everything bundled, so CLI won't work the same way
    REM Instead, show a message
    echo Note: CLI is not available in the packaged version.
    echo Please use the GUI by running: gpa_simulator.exe
    echo.
    pause
    exit /b 1
) else (
    REM We're in source mode, use venv if available
    if exist "!SCRIPT_DIR!venv\Scripts\activate.bat" (
        call "!SCRIPT_DIR!venv\Scripts\activate.bat"
        python main.py --cli
    ) else (
        echo.
        echo Error: Python environment not found.
        echo.
        echo For packaged version: Use gpa_simulator.exe for the GUI.
        echo For source version: Run BUILD_EXECUTABLE.bat to set up the environment.
        echo.
        pause
        exit /b 1
    )
)
pause
