import sqlite3, os, json
from typing import List, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'vault.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        program TEXT,
        duration INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS semesters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        semester_index INTEGER,
        total_cu INTEGER,
        gpa REAL,
        cgpa REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        semester_id INTEGER,
        name TEXT,
        credit_units INTEGER,
        grade_letter TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        params TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

def create_user(name: str, program: str = None, duration: int = None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, program, duration) VALUES (?, ?, ?)", (name, program, duration))
    uid = cur.lastrowid
    conn.commit()
    conn.close()
    return uid

def get_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def save_semester(user_id: int, semester_index: int, total_cu: int, gpa: float, cgpa: float, courses: List[Tuple[str,int,str]] = None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO semesters (user_id, semester_index, total_cu, gpa, cgpa) VALUES (?, ?, ?, ?, ?)", (user_id, semester_index, total_cu, gpa, cgpa))
    sem_id = cur.lastrowid
    if courses:
        for name, cu, letter in courses:
            cur.execute("INSERT INTO courses (semester_id, name, credit_units, grade_letter) VALUES (?, ?, ?, ?)", (sem_id, name, cu, letter))
    conn.commit()
    conn.close()
    return sem_id

def get_semesters_for_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM semesters WHERE user_id=? ORDER BY semester_index", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_courses_for_semester(semester_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses WHERE semester_id=?", (semester_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_scenario(user_id: int, name: str, params: dict) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO scenarios (user_id, name, params) VALUES (?, ?, ?)", (user_id, name, json.dumps(params)))
    sid = cur.lastrowid
    conn.commit()
    conn.close()
    return sid

def get_scenarios(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scenarios WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
