Frontend setup — Flutter (Windows) — Quick start

This file shows PowerShell-friendly steps to install Flutter on Windows, enable desktop targets, create a multiplatform Flutter project, and add the packages we plan to use.

1) Prerequisites
- Windows 10/11 (64-bit)
- Git installed and available on PATH
- PowerShell (the default shell works)
- Optionally: Visual Studio 2022 with "Desktop development with C++" workload (for Windows desktop builds)
- Android SDK / Android Studio if you want to build/run on Android

2) Manual Flutter install (recommended)
- Download the latest stable Windows Flutter SDK ZIP from https://flutter.dev/docs/get-started/install/windows
  - Open the above page and under "Get the Flutter SDK" click the stable channel link and download the Windows ZIP.
- Extract the ZIP to a folder you control, e.g.:

  D:\dev\flutter

- Add Flutter to PATH for the current session (PowerShell):

  # replace the path below with where you extracted flutter
  $env:PATH = "D:\dev\flutter\bin;" + $env:PATH

  # verify
  flutter --version
  flutter doctor

Note: to permanently add to PATH use System Environment Variables UI or setx (requires new shell session).

3) Enable desktop targets (if you plan to develop for Windows & Linux)

# Enable Windows and Linux
flutter config --enable-windows-desktop
flutter config --enable-linux-desktop

# Confirm devices availability
flutter devices

4) Create the Flutter project (multiplatform)

# From the folder where you want the project
cd "D:\GPA simulator"
flutter create gpa_simulator_ui
cd gpa_simulator_ui

# Add desktop targets metadata if needed
flutter create .

# Run the app on Windows
flutter run -d windows

5) Add recommended packages

flutter pub add flutter_riverpod go_router dio freezed_annotation json_annotation hive hive_flutter
flutter pub add --dev build_runner freezed json_serializable

Optional packages you may find useful:
- flutter_hooks
- adaptive_dialog
- responsive_framework
- flutter_native_splash
- flutter_launcher_icons

6) Useful commands

# Analyze
flutter analyze

# Format
flutter format .

# Run tests
flutter test

# Build windows release
flutter build windows

7) Quick project structure to create once scaffolded
- lib/main.dart
- lib/app.dart (router + providers)
- lib/src/core/api/client.dart
- lib/src/features/semester_input/
- lib/src/features/simulation/
- lib/src/shared/components/

8) Running against your backend
- In development, point the app to your API base URL (e.g., http://127.0.0.1:8000) via environment config or a settings provider.
- Example JSON payload for the /simulate endpoint:

{
  "num_courses": 7,
  "cus": [3,3,3,3,4,4,4],
  "target_gpa": 4.29,
  "exact_match": true,
  "exclude_F": true,
  "allow_A_if_needed": true,
  "max_results": 30
}

9) Next steps I can do for you (pick one)
- Scaffold the Flutter project in this workspace (I will create the basic lib files, sample UI screen, and run instructions). Note: I will only create source files; you must run Flutter locally to build.
- Create a small prototype UI (Semester Input + Run button + Results list) in Dart and place it under `gpa_simulator_ui/` in this workspace.
- Walk you through running Flutter on Windows / Android step-by-step interactively.

Which of the options above would you like me to proceed with?
