# GPA & CGPA Simulator (Offline Python Backend)

This project implements a modular offline Python backend for GPA & CGPA calculation,
simulations, and persistent local storage (SQLite). It exposes a **FastAPI** REST layer
so an external Flutter frontend can integrate easily, and also provides a **CLI** so you
can fully test functionality from the terminal before adding Flutter.

## Features
- GPA calculation (course-level)
- CGPA update and required-GPA solver
- Grade-combination generator for semester targets
- SQLite vault for users, semesters, courses, and saved scenarios
- FastAPI endpoints for all major operations (offline/local)
- CLI to exercise all core features without running the API server

## Run CLI
```bash
python3 main.py --cli
```

## Run API (local, offline)
```powershell
# install dependencies listed in requirements.txt first
pip install -r requirements.txt
# Run the API on all interfaces so mobile emulators/devices can reach it
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000/docs for Swagger UI.

Frontend
--------
- The standalone Flutter frontend for this backend lives in the sibling folder `../gpa_flutter_ui`.
- The backend previously contained a prototype Flutter UI which has been archived to `archive_backups/`.

Running the Flutter app
-----------------------
- If you run the Android emulator, use `http://10.0.2.2:8000` as the API base URL (this maps to host localhost).
- If you run on a physical device, replace the base URL with your host machine's LAN IP, e.g. `http://192.168.1.10:8000` and ensure your firewall allows the connection.

The FastAPI endpoints include `/cgpa/required` (required GPA calculation) and vault endpoints under `/vault/*` that the Flutter client can call.
