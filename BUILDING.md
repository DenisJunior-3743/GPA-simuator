# Building GPA Simulator for Multiple Platforms

This guide explains how to build the GPA/CGPA Simulator for Windows, Linux, macOS, and Android.

## Prerequisites

All platforms require:
- **Python 3.11+** (Python 3.12 recommended)
- **Git** for version control
- **pip** (Python package manager)

### Install Python Dependencies

```bash
pip install -r requirements.txt
pip install PyInstaller
```

## Building for Windows

### Using Batch Script (Easiest)

```bash
BUILD_EXECUTABLE.bat
```

This will:
1. Detect Python 3.12 or 3.23
2. Install dependencies
3. Run PyInstaller
4. Create `gpa-simulator-windows/` package
5. Package everything for distribution

### Manual Build (PowerShell)

```powershell
py -3.12 -m pip install --upgrade pip
pip install -r requirements.txt
pip install PyInstaller

py -3.12 -m PyInstaller gpa_simulator.spec --distpath dist_final --workpath build_work

# Package output
mkdir gpa-simulator-windows
copy dist_final\gpa_simulator.exe gpa-simulator-windows\
copy run_gpa_cli.bat gpa-simulator-windows\
copy gpa.ico gpa-simulator-windows\
```

**Output:** `dist_final/gpa_simulator.exe` (single-file executable, ~13 MB)

## Building for Linux

### Using Build Script

```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

### Manual Build (Bash)

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install PyInstaller

python3 -m PyInstaller gpa_simulator.spec --distpath dist_final --workpath build_work
chmod +x dist_final/gpa_simulator

# Package output
mkdir gpa-simulator-linux
cp dist_final/gpa_simulator gpa-simulator-linux/
cp gpa.ico gpa-simulator-linux/ 2>/dev/null || true
```

**Output:** `dist_final/gpa_simulator` (single-file executable, ~40 MB)

### Running on Linux

```bash
./gpa_simulator
```

The app will open at `http://localhost:5000` in your default browser.

## Building for macOS

### Using Build Script

```bash
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

### Manual Build (Bash)

```bash
python3 -m pip install --upgrade pip --break-system-packages
pip install -r requirements.txt --break-system-packages
pip install PyInstaller --break-system-packages

python3 -m PyInstaller gpa_simulator.spec --distpath dist_final --workpath build_work

# Package as app bundle
mkdir -p "dist_final/gpa_simulator.app/Contents/MacOS"
mkdir -p "dist_final/gpa_simulator.app/Contents/Resources"
cp dist_final/gpa_simulator "dist_final/gpa_simulator.app/Contents/MacOS/"
cp gpa.ico "dist_final/gpa_simulator.app/Contents/Resources/" 2>/dev/null || true
```

**Output:** `dist_final/gpa_simulator.app` (macOS app bundle)

### Running on macOS

```bash
open dist_final/gpa_simulator.app
```

Or double-click the app in Finder.

## Building for Android (Optional)

Android builds require **Buildozer** and Android SDK/NDK.

### Prerequisites

```bash
# Install Buildozer
pip install buildozer cython kivy

# Install Android SDK/NDK (or use buildozer setup)
buildozer android debug
```

### Build APK

Ensure `buildozer.spec` is configured, then:

```bash
buildozer android debug
```

**Output:** `bin/gpa-simulator-*.apk` (debug APK for testing)

### Building for Release

For production APK signing and optimization:

```bash
buildozer android release
```

## GitHub Actions CI/CD

This project includes automated CI/CD workflows that build on every push:

### Workflows

- **`.github/workflows/build-windows.yml`** – Builds Windows x86 & x64 executables
- **`.github/workflows/build-linux.yml`** – Builds Linux executable
- **`.github/workflows/build-macos.yml`** – Builds macOS app bundle
- **`.github/workflows/build-android.yml`** – Builds Android APK (if `buildozer.spec` present)

### Automatic Releases

When you push a tag like `v1.0`, GitHub Actions will:
1. Build all platforms automatically
2. Create a release with all artifacts attached
3. Upload binaries for download

### Pushing a Release

```bash
git tag v1.0
git push origin v1.0
```

This triggers all build workflows and creates a GitHub Release.

## Output Structure

After successful builds:

```
gpa-simulator-windows/
  ├── gpa_simulator.exe      # Main executable
  ├── run_gpa_cli.bat        # CLI launcher (optional)
  ├── gpa.ico               # Icon
  └── README.txt            # Instructions

gpa-simulator-linux/
  ├── gpa_simulator          # Main executable
  └── README.txt            # Instructions

dist_final/
  ├── gpa_simulator.app/    # macOS app bundle
  └── gpa_simulator         # Linux executable
```

## Troubleshooting

### PyInstaller not found

```bash
pip install PyInstaller
```

### Icon file not found

The build will continue without an icon. Ensure `gpa.ico` exists in the project root.

### Python version mismatch

On Windows, use the `py` launcher:
```bash
py -3.12 -m pip install ...
py -3.12 -m PyInstaller ...
```

On Linux/macOS:
```bash
python3.12 -m pip install ...
python3.12 -m PyInstaller ...
```

### Build fails on Linux with missing libraries

Install system dependencies:
```bash
sudo apt-get install python3-dev libssl-dev
```

### macOS security warning

On first run, macOS may block the app. Click "Open" in System Preferences > Security & Privacy.

## Build Customization

### Modifying the PyInstaller Spec

Edit `gpa_simulator.spec` to:
- Change console vs. windowed mode
- Add additional hidden imports
- Exclude unnecessary modules
- Change icon or UPX settings

### Environment-specific Builds

Create platform-specific PyInstaller specs:
- `gpa_simulator_windows.spec`
- `gpa_simulator_linux.spec`
- `gpa_simulator_macos.spec`

Then reference the appropriate spec in build scripts.

## Distribution

### Windows
- Distribute `gpa-simulator-windows.zip` or create an installer with NSIS/InnoSetup

### Linux
- Distribute as AppImage, Snap, or tarball
- `gpa-simulator-linux.tar.gz`

### macOS
- Distribute `gpa-simulator-macos.dmg` (created by build scripts)

### Android
- Upload APK to Google Play Store or distribute directly
- `gpa-simulator-*.apk`

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)

## Support

For issues or questions, open an issue on GitHub: [GPA-simuator Issues](https://github.com/DenisJunior-3743/GPA-simuator/issues)
