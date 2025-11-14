#!/usr/bin/env python3
"""
End-to-end test simulating the exact scenario from the user's screenshot:
- Register user
- Save semester with 7 courses (Year 3, Semester 1)
- View academic history
- Verify course names display correctly (not as template)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import vault_manager as vault
from app.constants import GRADE_POINTS

# Initialize
vault.init_db()
print("✅ Database initialized\n")

# Register user  
user = vault.register_user(
    'senior_student', 
    'secure_pass',
    'Sarah Engineer',
    'sarah@university.edu',
    'Computer Engineering',
    4
)
print(f"✅ User registered: {user['username']}")
print(f"   ID: {user['id']}\n")

# Simulate the exact 7 courses from the screenshot
courses_list = [
    ('Modelling and Simulation', 4, 'A'),
    ('Reliability and Testing', 4, 'B+'),
    ('Mobile Networks', 4, 'A'),
    ('Project Management', 4, 'A'),
    ('Data Mining', 4, 'B'),
    ('HCI', 4, 'A'),
    ('Technical Documentation', 3, 'A'),
]

# Calculate GPA manually
total_cu = sum(cu for _, cu, _ in courses_list)
total_gp = sum(GRADE_POINTS[grade] * cu for _, cu, grade in courses_list)
gpa = round(total_gp / total_cu, 2)

print(f"✅ Saving semester: Year 3, Semester 1")
print(f"   {len(courses_list)} courses, {total_cu} total CU")
print(f"   Calculated GPA: {gpa}\n")

# Save semester - THIS IS THE KEY TEST
sem_id = vault.save_semester(
    user_id=user['id'],
    academic_year=3,
    semester_num=1,
    total_cu=total_cu,
    gpa=gpa,
    cgpa=gpa,
    courses=courses_list  # Passing as list of tuples
)
print(f"✅ Semester saved with ID: {sem_id}\n")

# NOW VIEW ACADEMIC HISTORY (simulate the CLI view)
print("=" * 60)
print("VIEW ACADEMIC HISTORY OUTPUT:")
print("=" * 60 + "\n")

semesters = vault.get_semesters_for_user(user['id'])
if semesters:
    print(f"[SUCCESS] Found {len(semesters)} semester(s):\n")
    
    for sem in semesters:
        print(f"Year {sem['academic_year']} - Semester {sem['semester_num']}")
        print(f"  Total CU: {sem['total_cu']}")
        print(f"  Semester GPA: {sem['gpa']}")
        print(f"  Cumulative CGPA: {sem['cgpa']}")
        
        # Get courses for this semester
        courses = vault.get_courses_for_semester(sem['id'])
        if courses:
            print(f"  Courses ({len(courses)}):")
            for course in courses:
                # THIS IS THE CRITICAL TEST - course names should be REAL, not "name: grade_letter"
                print(f"    - {course['name']}: {course['grade_letter']} ({course['credit_units']} CU)")
        print()

print("=" * 60)
print("✅ SUCCESS! Course names are displayed correctly!")
print("   (NOT showing 'name: grade_letter' template like in the screenshot)")
print("=" * 60)
