import sqlite3, os, json
from typing import List, Tuple
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'vault.db')

# Store current logged-in user in memory
_current_user = None

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Set WAL mode and timeout at connection level
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Enable WAL mode for better concurrency and reduce lock contention
        cur.execute("PRAGMA journal_mode=WAL;")
        # Set busy timeout to 30 seconds in milliseconds
        cur.execute("PRAGMA busy_timeout = 30000;")
        # Increase cache size for better performance
        cur.execute("PRAGMA cache_size = 10000;")
        
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            program TEXT,
            duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS semesters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            academic_year INTEGER,
            semester_num INTEGER,
            total_cu INTEGER,
            gpa REAL,
            cgpa REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semester_id INTEGER NOT NULL,
            name TEXT,
            credit_units INTEGER,
            grade_letter TEXT,
            FOREIGN KEY(semester_id) REFERENCES semesters(id) ON DELETE CASCADE
        )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT,
            params TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )''')

        conn.commit()
    finally:
        conn.close()

def _hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, password: str, full_name: str = None, email: str = None, 
                  program: str = None, duration: int = None) -> dict:
    """Register a new user. Returns user dict on success, None on failure."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        hashed_pwd = _hash_password(password)
        cur.execute(
            "INSERT INTO users (username, password, full_name, email, program, duration) VALUES (?, ?, ?, ?, ?, ?)",
            (username, hashed_pwd, full_name, email, program, duration)
        )
        user_id = cur.lastrowid
        conn.commit()
        conn.close()
        return {'id': user_id, 'username': username, 'full_name': full_name, 'email': email, 'program': program, 'duration': duration}
    except sqlite3.IntegrityError:
        return None  # Username already exists

def login_user(username: str, password: str) -> dict:
    """Login user. Returns user dict on success, None on failure."""
    conn = get_connection()
    cur = conn.cursor()
    hashed_pwd = _hash_password(password)
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pwd))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_current_user() -> dict:
    """Get currently logged-in user."""
    global _current_user
    return _current_user

def set_current_user(user: dict):
    """Set the current logged-in user."""
    global _current_user
    _current_user = user

def logout_user():
    """Logout current user."""
    global _current_user
    _current_user = None

def create_user(name: str, program: str = None, duration: int = None) -> int:
    """Legacy function for creating user without auth."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, full_name, password, program, duration) VALUES (?, ?, ?, ?, ?)", 
                (name, name, _hash_password('guest'), program, duration))
    uid = cur.lastrowid
    conn.commit()
    conn.close()
    return uid

def get_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, full_name, email, program, duration FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def save_semester(user_id: int, academic_year: int, semester_num: int, total_cu: int, 
                  gpa: float, cgpa: float, courses: List[Tuple[str,int,str]] = None) -> int:
    """Save semester data with courses."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO semesters (user_id, academic_year, semester_num, total_cu, gpa, cgpa) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, academic_year, semester_num, total_cu, gpa, cgpa)
        )
        sem_id = cur.lastrowid
        if courses:
            for name, cu, letter in courses:
                cur.execute(
                    "INSERT INTO courses (semester_id, name, credit_units, grade_letter) VALUES (?, ?, ?, ?)",
                    (sem_id, name, cu, letter)
                )
        conn.commit()
        return sem_id
    finally:
        conn.close()

def get_semesters_for_user(user_id: int):
    """Get all semesters for a user ordered by academic year and semester."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM semesters WHERE user_id=? ORDER BY academic_year, semester_num",
            (user_id,)
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_latest_semester(user_id: int):
    """Get the latest semester for a user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM semesters WHERE user_id=? ORDER BY academic_year DESC, semester_num DESC LIMIT 1",
            (user_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_courses_for_semester(semester_id: int):
    """Get all courses for a semester."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM courses WHERE semester_id=?", (semester_id,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def save_scenario(user_id: int, name: str, params: dict) -> int:
    """Save a what-if scenario."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO scenarios (user_id, name, params) VALUES (?, ?, ?)",
            (user_id, name, json.dumps(params))
        )
        sid = cur.lastrowid
        conn.commit()
        return sid
    finally:
        conn.close()

def get_scenarios(user_id: int):
    """Get all scenarios for a user."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM scenarios WHERE user_id=?", (user_id,))
        rows = cur.fetchall()
        scenarios = []
        for r in rows:
            row_dict = dict(r)
            row_dict['params'] = json.loads(row_dict['params'])
            scenarios.append(row_dict)
        return scenarios
    finally:
        conn.close()

def calculate_current_cgpa(user_id: int) -> float:
    """Calculate cumulative CGPA from all semesters."""
    semesters = get_semesters_for_user(user_id)
    if not semesters:
        return 0.0
    
    total_gpa_weighted = 0.0
    total_cu = 0
    for sem in semesters:
        total_gpa_weighted += sem['gpa'] * sem['total_cu']
        total_cu += sem['total_cu']
    
    cgpa = total_gpa_weighted / total_cu if total_cu > 0 else 0.0
    from .utils import truncate
    return truncate(cgpa, 2)

def calculate_current_cgpa_with_new_semester(user_id: int, new_gpa: float, new_cu: int) -> float:
    """Calculate CGPA if a new semester is added (preview calculation)."""
    semesters = get_semesters_for_user(user_id)
    
    total_gpa_weighted = new_gpa * new_cu
    total_cu = new_cu
    
    for sem in semesters:
        total_gpa_weighted += sem['gpa'] * sem['total_cu']
        total_cu += sem['total_cu']
    
    cgpa = total_gpa_weighted / total_cu if total_cu > 0 else 0.0
    from .utils import truncate
    return truncate(cgpa, 2)

def get_total_cu_completed(user_id: int) -> int:
    """Get total credit units completed across all semesters for a user."""
    semesters = get_semesters_for_user(user_id)
    return sum(sem['total_cu'] for sem in semesters)

def get_semesters_summary(user_id: int):
    """Get a summary of all semesters for a user (for quick display and loading).
    
    Returns list of dicts with: {id, year, semester, gpa, cgpa, cu, course_count}
    """
    semesters = get_semesters_for_user(user_id)
    summary = []
    for sem in semesters:
        courses = get_courses_for_semester(sem['id'])
        summary.append({
            'id': sem['id'],
            'academic_year': sem['academic_year'],
            'semester_num': sem['semester_num'],
            'gpa': sem['gpa'],
            'cgpa': sem['cgpa'],
            'total_cu': sem['total_cu'],
            'course_count': len(courses) if courses else 0
        })
    return summary

def get_last_complete_semester_data(user_id: int) -> dict:
    """Get the most recently saved semester with all its courses.
    
    Returns: {id, academic_year, semester_num, gpa, cgpa, total_cu, courses: [...]}
    Or None if no semesters exist.
    """
    latest = get_latest_semester(user_id)
    if not latest:
        return None
    
    courses = get_courses_for_semester(latest['id'])
    return {
        'id': latest['id'],
        'academic_year': latest['academic_year'],
        'semester_num': latest['semester_num'],
        'gpa': latest['gpa'],
        'cgpa': latest['cgpa'],
        'total_cu': latest['total_cu'],
        'courses': courses if courses else []
    }
