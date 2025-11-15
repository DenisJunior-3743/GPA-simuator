# GPA/CGPA Simulator - Multi-Platform Build Guide

This project is built for **offline access** on Windows, Linux, macOS, and can be adapted for Android and iOS.

## Quick Start

### Windows
```bash
# Option 1: Use the batch launcher (easiest)
run_simulator.bat

# Option 2: Run standalone executable
dist/gpa_simulator/gpa_simulator.exe
```

### Linux
```bash
# Extract and run AppImage
./gpa-simulator-x86_64.AppImage

# Or extract tar.gz
tar xzf gpa-simulator-linux.tar.gz
cd gpa_simulator
./gpa_simulator
```

### macOS
```bash
# Open the DMG file and drag app to Applications
# Then run: 
/Applications/GPA\ Simulator.app/Contents/MacOS/gpa_simulator
```

---

## Build Instructions

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Git

### Setup Environment
```bash
# Clone the repository
git clone https://github.com/DenisJunior-3743/GPA-simuator.git
cd gpa_cgpa_simulator_api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

---

## Building Executables

### Option 1: GitHub Actions (Automated - Recommended)
The `.github/workflows/cross-platform-build.yml` automatically builds all platforms on every push to `simulator_gui` branch or when you tag a release (`v1.0.0`).

**Steps:**
1. Push code to GitHub
2. Go to **Actions** tab
3. Find the **Build Cross-Platform Releases** workflow
4. Download artifacts or create a tagged release for automatic uploads

### Option 2: Local Build

#### Windows
```bash
pyinstaller gpa_simulator.spec --distpath "./dist-windows"
# Output: dist-windows/gpa_simulator/gpa_simulator.exe
```

#### Linux
```bash
pyinstaller gpa_simulator.spec --distpath "./dist-linux" --onedir
# Download linuxdeploy to create AppImage
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod +x linuxdeploy-x86_64.AppImage
./linuxdeploy-x86_64.AppImage --appdir=dist-linux/gpa_simulator --create-appimage
# Output: gpa-simulator-x86_64.AppImage
```

#### macOS
```bash
pyinstaller gpa_simulator.spec --distpath "./dist-macos" --windowed
# Create DMG (optional)
hdiutil create -volname "GPA Simulator" -srcfolder dist-macos -ov -format UDZO gpa-simulator-macos.dmg
# Output: dist-macos/gpa_simulator.app
```

---

## Android & iOS (Alternative Approaches)

### Android Option 1: Kivy + Buildozer
For a native Android experience, we can wrap the Flask app using Kivy:

**Setup:**
```bash
pip install kivy buildozer cython
```

**Build:**
```bash
# Create Kivy wrapper in kivy_app/ directory
buildozer android debug
# Output: kivy_app/bin/gpa-simulator-debug.apk
```

### Android Option 2: Web Wrapper
Use **Flutter** or **React Native** to create a WebView wrapper:
- Bundles a minimal web server (Flask)
- Offline-capable with local SQLite database
- Can be distributed via Google Play Store

### iOS Option 1: Native Web App
Use **Swift** with WKWebView to wrap the Flask app:
```swift
import WebKit
// Load local Flask server on port 5000
webView.load(URLRequest(url: URL(string: "http://127.0.0.1:5000")!))
```

### iOS Option 2: Progressive Web App (PWA)
Convert to a PWA and use **Capacitor** or **Cordova**:
```bash
npm install -g @ionic/cli
ionic start gpa-simulator --template=angular
# Add Capacitor for native wrapper
```

---

## Offline Database Setup

All platforms use a **local SQLite database** (`vault`) stored in:
- **Windows**: `%APPDATA%/gpa_simulator/`
- **Linux**: `~/.local/share/gpa_simulator/`
- **macOS**: `~/Library/Application Support/gpa_simulator/`

No internet connection required after initial download!

---

## Distribution

### GitHub Releases
Tag your code to trigger automatic release builds:
```bash
git tag v1.0.0
git push origin v1.0.0
```

All platforms build automatically and upload to GitHub Releases!

### Manual Distribution
1. Build on each platform
2. Create `releases/` folder:
   ```
   releases/
   ├── gpa-simulator-windows.zip
   ├── gpa-simulator-linux.tar.gz
   ├── gpa-simulator-macos.dmg
   └── gpa-simulator-android.apk
   ```
3. Upload to GitHub Releases or your website

---

## Platform-Specific Notes

### Windows
- Antivirus may flag unsigned .exe files (this is normal)
- Include `python313.dll` alongside the executable
- Can be installed via Windows Installer (`.msi`) if needed

### Linux
- AppImage is portable across all distributions
- Make it executable: `chmod +x gpa-simulator-x86_64.AppImage`
- May need FUSE library: `sudo apt install libfuse2`

### macOS
- Unsigned `.app` will warn on first run
- Can be notarized for full trust (requires Apple Developer account)
- `.dmg` provides a professional installer experience

### Android
- Install from file (Settings → Security → Unknown sources)
- Alternative: Upload to Google Play Store for distribution
- Requires Android 8.0+ (API 26)

### iOS
- Requires macOS with Xcode for building
- Can be distributed via TestFlight or App Store
- Requires Apple Developer account (~$99/year)

---

## Troubleshooting

**"Module not found" error when running executable**
- PyInstaller may have missed hidden imports
- Add to `gpa_simulator.spec` hiddenimports: `['flask', 'jinja2', 'sqlite3']`

**Port 5000 already in use**
- Change port in `ui_app.py`: `app.run(port=5001)`

**SSL certificate warnings (Linux)**
- Use `--onedir` instead of `--onefile` for better library detection

**macOS "app is damaged" warning**
- App isn't code-signed; use: `codesign -s - path/to/app`

---

## Next Steps

1. **Test locally**: Run `run_simulator.bat` or `python ui_app.py`
2. **Build for your platform**: Follow the build instructions above
3. **Push to GitHub**: Enable Actions to auto-build all platforms
4. **Create release**: Tag and push to generate downloadable executables

---

## Support Matrix

| Platform | Status | Format | Offline | Notes |
|----------|--------|--------|---------|-------|
| Windows | ✅ Ready | .exe / .zip | Yes | PyInstaller + batch launcher |
| Linux | ✅ Ready | AppImage / .tar.gz | Yes | linuxdeploy portable |
| macOS | ✅ Ready | .app / .dmg | Yes | PyInstaller with bundle |
| Android | 🟡 WIP | .apk | Yes | Kivy/Buildozer wrapper needed |
| iOS | 🟡 WIP | .ipa | Yes | Swift/Capacitor wrapper needed |

---

**Build Status**: GitHub Actions automatically builds all platforms on push. Check the [Releases](https://github.com/DenisJunior-3743/GPA-simuator/releases) page for pre-built binaries!
