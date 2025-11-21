@echo off
REM Build GPA Simulator Executable
REM Run this batch file to create a single-file .exe

title Building GPA Simulator Executable...

echo.
echo ========================================
echo  GPA Simulator - Building Executable
echo ========================================
echo.

REM Detect Python
echo Checking for Python 3.12 or 3.23...
py -3.23 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=py -3.23
    echo Found Python 3.23
    goto :found_python
)

py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON=py -3.12
    echo Found Python 3.12
    goto :found_python
)

echo ERROR: Python 3.23 or 3.12 not found
echo Please install one of these versions from python.org
pause
exit /b 1

:found_python
echo.
echo Installing dependencies...
%PYTHON% -m pip install --quiet Flask Werkzeug PyInstaller

echo.
echo Building executable with PyInstaller...
echo (This may take a few minutes, please wait...)
echo.

REM Clean old builds
if exist dist_final rmdir /s /q dist_final
if exist build_pyinstaller rmdir /s /q build_pyinstaller

REM Run PyInstaller
%PYTHON% -m PyInstaller gpa_simulator.spec --onefile --distpath dist_final --workpath build_pyinstaller

REM Check if exe was created
if not exist dist_final\gpa_simulator.exe (
    echo.
    echo ERROR: Build failed! Executable not created.
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Executable created!
echo ========================================
echo.

REM Create output package
if exist gpa-simulator-windows rmdir /s /q gpa-simulator-windows
mkdir gpa-simulator-windows

echo Creating package...
copy dist_final\gpa_simulator.exe gpa-simulator-windows\ >nul
copy run_gpa_cli.bat gpa-simulator-windows\ >nul 2>&1
copy gpa.ico gpa-simulator-windows\ >nul 2>&1

(
    echo GPA and CGPA Simulator - Windows Executable
    echo.
    echo CONTENTS:
    echo - gpa_simulator.exe    : Main executable (double-click to run^)
    echo - run_gpa_cli.bat      : Optional launcher script
    echo - gpa.ico             : Application icon
    echo.
    echo HOW TO RUN:
    echo 1. Double-click gpa_simulator.exe, OR
    echo 2. Run run_gpa_cli.bat
    echo.
    echo The application runs on http://localhost:5000
    echo No additional files or installation needed!
) > gpa-simulator-windows\README.txt

echo.
echo Package contents:
dir /B gpa-simulator-windows\
echo.
echo ========================================
echo Ready to distribute! 
echo Folder: gpa-simulator-windows\
echo ========================================
echo.
pause
