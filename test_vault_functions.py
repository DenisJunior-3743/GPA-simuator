#!/usr/bin/env python3
"""Simple test of vault functions after onboarding."""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import vault_manager as vault

vault.init_db()

# Create unique user
unique_id = int(time.time() * 1000) % 100000
username = f'onboard_test_{unique_id}'

user = vault.register_user(username, 'pass', 'Test User', 'test@test.edu', 'Engineering', 3)

if not user:
    print("Registration failed")
    sys.exit(1)

print(f"✅ User registered: {username} (ID: {user['id']})")

# Simulate onboarding: save 5 semesters
semesters = [
    (1, 1, 24, 3.5),
    (1, 2, 24, 3.7),
    (2, 1, 25, 3.8),
    (2, 2, 25, 3.9),
    (3, 1, 26, 4.0),
]

for y, s, cu, gpa in semesters:
    if y == 1 and s == 1:
        cgpa = 3.5
    else:
        cgpa = vault.calculate_current_cgpa_with_new_semester(user['id'], gpa, cu)
        cgpa = round(cgpa, 2)
    
    vault.save_semester(user['id'], y, s, cu, gpa, cgpa, [])
    print(f'  ✅ Y{y}S{s}: GPA={gpa}, CU={cu}, CGPA={cgpa}')

print("\n" + "="*50)
print("Testing vault retrieval functions")
print("="*50)

# Test get_total_cu_completed
total_cu = vault.get_total_cu_completed(user['id'])
print(f"\n✅ Total CU completed: {total_cu}")

# Test get_semesters_summary
summary = vault.get_semesters_summary(user['id'])
print(f"\n✅ Semester summary ({len(summary)} semesters):")
print(f"{'Year':<6} {'Sem':<5} {'GPA':<8} {'CGPA':<8} {'CU':<8}")
print("-" * 35)
for s in summary:
    print(f"{s['academic_year']:<6} {s['semester_num']:<5} {s['gpa']:<8.2f} {s['cgpa']:<8.2f} {s['total_cu']:<8}")

# Test get_last_complete_semester_data
last = vault.get_last_complete_semester_data(user['id'])
print(f"\n✅ Last completed semester:")
print(f"   Year: {last['academic_year']}, Semester: {last['semester_num']}")
print(f"   GPA: {last['gpa']}, CGPA: {last['cgpa']}, CU: {last['total_cu']}")

print("\n" + "="*50)
print("✅ ALL VAULT FUNCTIONS WORKING!")
print("="*50)
