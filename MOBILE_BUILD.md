# Building for Android & iOS

## Android Build Setup

### Method 1: Kivy + Buildozer (Recommended for Flask apps)

**Install Tools:**
```bash
pip install kivy buildozer cython
sudo apt-get install build-essential git python3-dev ffmpeg \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
  zlib1g-dev
```

**Create Kivy App Wrapper** (`kivy_app/main.py`):
```python
from kivy.app import App
from kivy.garden.webview import WebView
from kivy.uix.boxlayout import BoxLayout
import threading
import subprocess
import sys
import os

# Add parent directory to path to import Flask app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GPASimulatorApp(App):
    def build(self):
        layout = BoxLayout()
        webview = WebView()
        webview.url = 'http://127.0.0.1:5000'
        layout.add_widget(webview)
        
        # Start Flask server in background thread
        def start_flask():
            from ui_app import app as flask_app
            flask_app.run(host='127.0.0.1', port=5000, 
                         debug=False, use_reloader=False, 
                         threaded=True)
        
        thread = threading.Thread(target=start_flask, daemon=True)
        thread.start()
        
        return layout

if __name__ == '__main__':
    GPASimulatorApp().run()
```

**Create buildozer.spec:**
```bash
cd kivy_app
buildozer init
```

**Edit buildozer.spec:**
```ini
[app]
title = GPA Simulator
package.name = gpasimulator
package.domain = org.gpasim

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db

version = 1.0.0

requirements = python3,kivy,flask,werkzeug,sqlite3,jinja2

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25c
```

**Build APK:**
```bash
buildozer android debug
# Output: bin/gpasimulator-1.0.0-debug.apk
```

---

## iOS Build Setup

### Method 1: Swift + WKWebView (Native App)

**Requirements:**
- macOS with Xcode 14+
- iOS 14+ target

**Create Xcode Project:**
1. Open Xcode → Create new iOS App
2. Choose "Storyboard" (simpler for webview)
3. Configure settings:
   - Product Name: `GPA Simulator`
   - Team ID: (if publishing to App Store)
   - Minimum Deployment: iOS 14.0

**ViewController.swift:**
```swift
import UIKit
import WebKit

class ViewController: UIViewController, WKNavigationDelegate {
    var webView: WKWebView!
    var serverProcess: Process?
    
    override func loadView() {
        let webConfiguration = WKWebViewConfiguration()
        webView = WKWebView(frame: .zero, configuration: webConfiguration)
        webView.navigationDelegate = self
        view = webView
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Start Flask server
        startFlaskServer()
        
        // Wait for server to start
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            let myURL = URL(string: "http://127.0.0.1:5000")!
            let myRequest = URLRequest(url: myURL)
            self.webView.load(myRequest)
        }
    }
    
    func startFlaskServer() {
        serverProcess = Process()
        serverProcess?.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        serverProcess?.arguments = [
            Bundle.main.path(forResource: "ui_app", ofType: "py") ?? ""
        ]
        try? serverProcess?.run()
    }
    
    deinit {
        serverProcess?.terminate()
    }
}
```

**Build & Deploy:**
```bash
# Development (TestFlight)
xcodebuild -scheme "GPA Simulator" -configuration Release \
  -derivedDataPath ./build

# App Store
# Use Xcode's Archive → Distribute App Flow
```

---

### Method 2: Capacitor + Flutter (Cross-Platform Hybrid)

**Setup Capacitor:**
```bash
npm install -g @capacitor/cli
ionic start gpa-simulator --template=angular
cd gpa-simulator

# Add iOS
ionic capacitor add ios

# Build web app
ionic build

# Sync to iOS
npx cap sync ios

# Open in Xcode
npx cap open ios
```

**main.ts** (run Flask on load):
```typescript
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';
import { Capacitor } from '@capacitor/core';
import { Http } from '@capacitor-community/http';

platformBrowserDynamic().bootstrapModule(AppModule);

// Check if running on mobile
if (Capacitor.isNativePlatform()) {
  // Request to start Flask server
  Http.request({
    method: 'POST',
    url: 'http://127.0.0.1:5000/start',
  });
}
```

---

## GitHub Actions for Android

Add to `.github/workflows/cross-platform-build.yml`:

```yaml
build-android:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install buildozer
      run: |
        pip install buildozer cython kivy
        sudo apt-get update && sudo apt-get install -y openjdk-11-jdk
    - name: Build APK
      run: |
        cd kivy_app
        buildozer android debug
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: android
        path: kivy_app/bin/*.apk
```

---

## Distribution

### Android
1. **Google Play Store**: Upload signed .apk / .aab
2. **Direct Distribution**: Share .apk file (users enable "Unknown sources")
3. **F-Droid**: Open-source alternative app store

### iOS
1. **App Store**: Use Apple's App Store distribution
2. **TestFlight**: Beta testing with Apple's service
3. **Ad-hoc**: Direct distribution to registered devices
4. **Enterprise**: Internal company distribution

---

## Important Notes

⚠️ **Offline Database Path** (Android/iOS):
- Use `getApplicationContext().getFilesDir()` (Android)
- Use `NSDocumentDirectory` (iOS)
- Ensure database path works in app sandbox

⚠️ **Port Access**:
- Mobile browsers may not allow `http://127.0.0.1`
- Use `http://localhost:5000` instead

⚠️ **Permissions**:
- Android: Request `INTERNET` and `WRITE_EXTERNAL_STORAGE` if exporting data
- iOS: No special permissions needed for localhost

---

## Testing

```bash
# Test APK on emulator
adb install bin/gpasimulator-1.0.0-debug.apk
adb logcat | grep flask

# Test iOS on simulator
xcodebuild -scheme "GPA Simulator" -configuration Debug \
  -sdk iphonesimulator -derivedDataPath ./build
```

Done! This setup provides **offline, platform-native versions** for Android and iOS. 🚀
