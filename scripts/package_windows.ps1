
# PowerShell: Build Windows executable using PyInstaller

param([string]$SpecFile = "gpa_simulator.spec")

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $root

# Find Python 3.23 or 3.12
$pythonCmd = $null

Write-Host "Searching for Python 3.23..."
try {
    $v = & py -3.23 --version 2>&1
    if ($v -match "3.23") { $pythonCmd = "py -3.23" }
} catch {}

if (-not $pythonCmd) {
    Write-Host "Searching for Python 3.12..."
    try {
        $v = & py -3.12 --version 2>&1
        if ($v -match "3.12") { $pythonCmd = "py -3.12" }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Error "Python 3.23 or 3.12 not found"
    exit 1
}

Write-Host "Found: $pythonCmd"

# Create venv
$venvDir = '.venv_build'
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating venv..."
    Invoke-Expression "$pythonCmd -m venv $venvDir"
}

# Install deps
Write-Host "Installing dependencies..."
$activate = Join-Path $venvDir 'Scripts\Activate.ps1'
$cmd1 = @"
. "$activate"
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt pyinstaller
"@
Invoke-Expression $cmd1

# Build exe
Write-Host "Running PyInstaller..."
$distDir = "dist_final"
$cmd2 = @"
. "$activate"
pyinstaller "$SpecFile" --onefile --distpath "$distDir" --buildpath build_pyinstaller --specpath build_pyinstaller
"@
Invoke-Expression $cmd2

# Verify
$exePath = Join-Path $distDir "gpa_simulator.exe"
if (-not (Test-Path $exePath)) {
    Write-Error "Build failed - exe not found at $exePath"
    exit 1
}

Write-Host "Executable created at: $exePath"

# Package
$outFolder = "gpa-simulator-windows"
if (Test-Path $outFolder) { Remove-Item -Recurse -Force $outFolder }
New-Item -ItemType Directory -Path $outFolder | Out-Null

Copy-Item $exePath $outFolder -Force
Write-Host "Copied exe to output folder"

if (Test-Path "run_gpa_cli.bat") {
    Copy-Item "run_gpa_cli.bat" $outFolder -Force
    Write-Host "Copied launcher"
}

if (Test-Path "gpa.ico") {
    Copy-Item "gpa.ico" $outFolder -Force
    Write-Host "Copied icon"
}

$readmeFile = Join-Path $outFolder "README.txt"
@"
GPA and CGPA Simulator

This is a self-contained executable. Just run gpa_simulator.exe!

Contents:
- gpa_simulator.exe : Main application
- run_gpa_cli.bat   : Optional launcher
- gpa.ico          : Application icon

Double-click the .exe to start. Your browser will open automatically.
"@ | Out-File -Encoding UTF8 $readmeFile

# Zip
$zipPath = "${outFolder}.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path "$outFolder\*" -DestinationPath $zipPath -Force
Write-Host "Created: $zipPath"

Pop-Location
Write-Host ""
Write-Host "Build complete! Check current directory for .zip file."
