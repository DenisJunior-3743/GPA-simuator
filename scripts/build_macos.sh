#!/bin/bash
# Build GPA Simulator for macOS using PyInstaller

set -e

echo "========================================"
echo " GPA Simulator - macOS Build"
echo "========================================"
echo

# Detect Python
if command -v python3.12 &> /dev/null; then
    PYTHON=python3.12
    echo "Found Python 3.12"
elif command -v python3 &> /dev/null; then
    PYTHON=python3
    echo "Found Python 3"
else
    echo "ERROR: Python 3 not found"
    exit 1
fi

echo
echo "Installing dependencies..."
$PYTHON -m pip install --quiet Flask Werkzeug PyInstaller

echo
echo "Building executable with PyInstaller..."
echo "(This may take a few minutes, please wait...)"
echo

# Clean old builds
rm -rf dist_final build_work

# Run PyInstaller - for macOS, use --onedir or --onefile
$PYTHON -m PyInstaller gpa_simulator.spec --distpath dist_final --workpath build_work

# Check if app bundle was created
if [ ! -d "dist_final/gpa_simulator.app" ]; then
    echo
    echo "ERROR: Build failed! App bundle not created."
    exit 1
fi

echo
echo "========================================"
echo "SUCCESS! App bundle created!"
echo "========================================"
echo

# Create output package
rm -rf gpa-simulator-macos
mkdir -p gpa-simulator-macos

echo "Creating package..."
cp -r dist_final/gpa_simulator.app gpa-simulator-macos/

cat > gpa-simulator-macos/README.txt << 'EOF'
GPA and CGPA Simulator - macOS Application

CONTENTS:
- gpa_simulator.app : Main application bundle

HOW TO RUN:
1. Double-click gpa_simulator.app
2. Or: open gpa_simulator.app from Terminal

The application runs on http://localhost:5000
No additional files or installation needed!

Note: On first run, macOS may ask for security permissions.
If prompted, click "Open" to allow the application to run.
EOF

echo
echo "Package contents:"
ls -la gpa-simulator-macos/
echo
echo "========================================"
echo "Ready to distribute!"
echo "Folder: gpa-simulator-macos/"
echo "========================================"
echo
