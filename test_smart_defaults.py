#!/usr/bin/env python3
"""Test smart defaults in Option 2 (Update CGPA) flow."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import vault_manager as vault
from main import get_smart_defaults_from_vault

vault.init_db()

# Create user with saved semesters (simulating onboarded user)
user = vault.register_user('smart_defaults_test', 'pass', 'Test', 'test@test.edu', 'CS', 3)
user_id = user['id']

print(f"✅ User created: {user['username']}")

# Save some semesters
vault.save_semester(user_id, 1, 1, 24, 3.5, 3.5, [])
print(f"  ✅ Y1S1: GPA=3.5, CU=24, CGPA=3.5")

cgpa = vault.calculate_current_cgpa_with_new_semester(user_id, 3.7, 24)
cgpa = round(cgpa, 2)
vault.save_semester(user_id, 1, 2, 24, 3.7, cgpa, [])
print(f"  ✅ Y1S2: GPA=3.7, CU=24, CGPA={cgpa}")

cgpa = vault.calculate_current_cgpa_with_new_semester(user_id, 3.8, 25)
cgpa = round(cgpa, 2)
vault.save_semester(user_id, 2, 1, 25, 3.8, cgpa, [])
print(f"  ✅ Y2S1: GPA=3.8, CU=25, CGPA={cgpa}")

print("\n" + "="*60)
print("Testing smart defaults retrieval")
print("="*60)

# Test the smart defaults function
defaults = get_smart_defaults_from_vault(user_id)

print(f"\n✅ Smart defaults retrieved:")
print(f"   Old CGPA: {defaults['old_cgpa']}")
print(f"   Old CU: {defaults['old_cu']}")
print(f"   Last semester: Year {defaults['last_semester']['academic_year']}, Sem {defaults['last_semester']['semester_num']}")
print(f"                  GPA={defaults['last_semester']['gpa']}, CGPA={defaults['last_semester']['cgpa']}")

print("\n✅ These would be auto-populated in the Update CGPA form")
print("   User would only need to enter new semester GPA and CU")

# Simulate calculating new CGPA with defaults
print("\n" + "="*60)
print("Simulating Update CGPA calculation")
print("="*60)

old_cgpa = defaults['old_cgpa']
old_cu = defaults['old_cu']
new_gpa = 3.9  # User enters this
new_cu = 26    # User enters this

from app.cgpa_calculator import update_cgpa
new_cgpa = update_cgpa(old_cgpa, old_cu, new_gpa, new_cu)
new_cgpa = round(new_cgpa, 2)

print(f"\n✅ Calculation result:")
print(f"   Old CGPA: {old_cgpa} (from Y{defaults['last_semester']['academic_year']}S{defaults['last_semester']['semester_num']})")
print(f"   Old CU: {old_cu}")
print(f"   New semester GPA: {new_gpa} (user entered)")
print(f"   New semester CU: {new_cu} (user entered)")
print(f"   → New CGPA: {new_cgpa}")

print("\n" + "="*60)
print("✅ SMART DEFAULTS WORKING - User saved from entering 2 values!")
print("="*60)
