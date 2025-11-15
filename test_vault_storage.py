#!/usr/bin/env python3
"""Quick test script for save/view semester functionality."""

import sqlite3
import sys
sys.path.insert(0, '/d/GPA simulator/gpa_cgpa_simulator_api')

from app import vault_manager as vault

# Initialize DB
vault.init_db()

# Register user
user = vault.register_user('testuser6', 'password123', 'Test User', 'test@test.com', 'CS', 3)
print(f"✅ User created: {user['username']}")

# Create courses as tuples (name, cu, grade_letter)
courses_tuples = [
    ('Calculus I', 4, 'A'),
    ('Physics I', 4, 'B+'),
    ('Chemistry I', 3, 'B'),
]

# Save semester
sem_id = vault.save_semester(
    user_id=user['id'],
    academic_year=1,
    semester_num=1,
    total_cu=11,
    gpa=4.3,
    cgpa=4.3,
    courses=courses_tuples
)
print(f"✅ Semester saved: ID {sem_id}")

# Verify by retrieving courses
courses = vault.get_courses_for_semester(sem_id)
print(f"\n✅ Retrieved {len(courses)} courses:")
for course in courses:
    print(f"  - {course['name']}: {course['grade_letter']} ({course['credit_units']} CU)")

# Get semesters for user
semesters = vault.get_semesters_for_user(user['id'])
print(f"\n✅ User has {len(semesters)} semester(s)")
for sem in semesters:
    print(f"  Year {sem['academic_year']}, Sem {sem['semester_num']}: GPA {sem['gpa']}, CGPA {sem['cgpa']}")

print("\n✅ All tests passed!")
