#!/bin/bash
# Build GPA Simulator for Linux using PyInstaller

set -e

echo "========================================"
echo " GPA Simulator - Linux Build"
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

# Run PyInstaller
$PYTHON -m PyInstaller gpa_simulator.spec --distpath dist_final --workpath build_work

# Check if exe was created
if [ ! -f "dist_final/gpa_simulator" ]; then
    echo
    echo "ERROR: Build failed! Executable not created."
    exit 1
fi

# Make executable
chmod +x dist_final/gpa_simulator

echo
echo "========================================"
echo "SUCCESS! Executable created!"
echo "========================================"
echo

# Create output package
rm -rf gpa-simulator-linux
mkdir -p gpa-simulator-linux

echo "Creating package..."
cp dist_final/gpa_simulator gpa-simulator-linux/
cp gpa.ico gpa-simulator-linux/ 2>/dev/null || true

cat > gpa-simulator-linux/README.txt << 'EOF'
GPA and CGPA Simulator - Linux Executable

CONTENTS:
- gpa_simulator     : Main executable
- gpa.ico          : Application icon

HOW TO RUN:
1. ./gpa_simulator (make sure it's executable)
2. Or: chmod +x gpa_simulator && ./gpa_simulator

The application runs on http://localhost:5000
No additional files or installation needed!
EOF

echo
echo "Package contents:"
ls -la gpa-simulator-linux/
echo
echo "========================================"
echo "Ready to distribute!"
echo "Folder: gpa-simulator-linux/"
echo "========================================"
echo
