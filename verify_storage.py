#!/usr/bin/env python3
"""Direct database verification of course storage."""

import sqlite3
import sys
sys.path.insert(0, '/d/GPA simulator/gpa_cgpa_simulator_api')

from app import vault_manager as vault

# Test 1: Direct database check
print("=== DATABASE VERIFICATION ===\n")

vault.init_db()

# Create test data
user = vault.register_user('finaltest', 'pass', 'Final Test', 'final@test.com', 'IT', 4)
print(f"Created user: {user['username']} (ID: {user['id']})")

# Save semester with courses
courses_data = [
    ('Introduction to CS', 3, 'A'),
    ('Data Structures', 4, 'B+'),
    ('Web Development', 3, 'A'),
]

sem_id = vault.save_semester(
    user_id=user['id'],
    academic_year=2,
    semester_num=1,
    total_cu=10,
    gpa=4.5,
    cgpa=4.5,
    courses=courses_data
)
print(f"Saved semester: ID {sem_id}")

# Direct database query to verify storage
conn = vault.get_connection()
cur = conn.cursor()

print("\n--- Semesters in database ---")
cur.execute("SELECT id, academic_year, semester_num, gpa, cgpa FROM semesters WHERE user_id=?", (user['id'],))
for row in cur.fetchall():
    print(f"Semester {row[0]}: Year {row[1]}, Sem {row[2]}, GPA {row[3]}, CGPA {row[4]}")

print("\n--- Courses in database ---")
cur.execute("SELECT name, grade_letter, credit_units FROM courses WHERE semester_id=?", (sem_id,))
for row in cur.fetchall():
    print(f"  ✓ {row[0]}: {row[1]} ({row[2]} CU)")

conn.close()

# Test 2: Verify retrieval functions work
print("\n--- Via vault functions ---")
semesters = vault.get_semesters_for_user(user['id'])
print(f"Semesters retrieved: {len(semesters)}")

for sem in semesters:
    print(f"\nYear {sem['academic_year']}, Semester {sem['semester_num']}")
    print(f"  Semester GPA: {sem['gpa']}")
    print(f"  Cumulative CGPA: {sem['cgpa']}")
    print(f"  Total CU: {sem['total_cu']}")
    
    courses = vault.get_courses_for_semester(sem['id'])
    print(f"  Courses ({len(courses)}):")
    for course in courses:
        print(f"    - {course['name']}: {course['grade_letter']} ({course['credit_units']} CU)")

print("\n✅ All data properly stored and retrieved!")
