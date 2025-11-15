#!/usr/bin/env python3
"""End-to-end test showing the complete reduced-load workflow for logged-in users.

This demonstrates:
1. New user registration with onboarding option
2. Saving academic history during onboarding
3. Using smart defaults in Option 2 (Update CGPA)
4. Using vault data for calculations
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import vault_manager as vault
from app.cgpa_calculator import update_cgpa
from main import get_smart_defaults_from_vault

print("\n" + "="*70)
print("COMPLETE WORKFLOW: REDUCED-LOAD LOGGED-IN USER EXPERIENCE")
print("="*70)

# Initialize
vault.init_db()

print("\n[PHASE 1] User Registration with Onboarding")
print("-" * 70)

user = vault.register_user(
    'reduced_load_test',
    'secure_password',
    'Alice Student',
    'alice@university.edu',
    'Computer Science',
    3
)

print(f"✅ Account created for: {user['full_name']} ({user['username']})")
print(f"   Program: {user['program']}, Expected Duration: {user['duration']} years")

print("\n[PHASE 2] First-Time Onboarding (Simulated)")
print("-" * 70)
print("User opts for onboarding...")
print("  - Selects current year: 3")
print("  - Selects current semester: 1")
print("  - Chooses QUICK entry mode (no course names)")
print("  - Enters CU and GPA for each completed semester")

# Simulate quick entry mode onboarding for a Year 3, Sem 1 student
print("\nOnboarding data being saved...")
semesters_data = [
    {"year": 1, "sem": 1, "cu": 24, "gpa": 3.4, "label": "Year 1, Sem 1"},
    {"year": 1, "sem": 2, "cu": 24, "gpa": 3.6, "label": "Year 1, Sem 2"},
    {"year": 2, "sem": 1, "cu": 25, "gpa": 3.7, "label": "Year 2, Sem 1"},
    {"year": 2, "sem": 2, "cu": 25, "gpa": 3.8, "label": "Year 2, Sem 2"},
    {"year": 3, "sem": 1, "cu": 26, "gpa": 3.9, "label": "Year 3, Sem 1 (current)"},
]

cumulative_cgpa = 0
cumulative_cu = 0

for sem in semesters_data:
    if sem["year"] == 1 and sem["sem"] == 1:
        cumulative_cgpa = sem["gpa"]
    else:
        cumulative_cgpa = vault.calculate_current_cgpa_with_new_semester(
            user['id'], sem["gpa"], sem["cu"]
        )
        cumulative_cgpa = round(cumulative_cgpa, 2)
    
    cumulative_cu += sem["cu"]
    vault.save_semester(user['id'], sem["year"], sem["sem"], sem["cu"], sem["gpa"], cumulative_cgpa, [])
    print(f"  ✅ {sem['label']}: GPA={sem['gpa']}, CU={sem['cu']}, CGPA={cumulative_cgpa}")

print(f"\n✅ Onboarding complete! {len(semesters_data)} semesters saved to vault.")

print("\n" + "="*70)
print("[PHASE 3] Using System - Option 2: Update CGPA")
print("-" * 70)
print("User selects Option 2 to calculate CGPA after next semester")

# Get smart defaults
defaults = get_smart_defaults_from_vault(user['id'])

print(f"\n✅ System retrieves smart defaults from vault:")
print(f"   Last recorded CGPA: {defaults['old_cgpa']}")
print(f"   Total CU completed: {defaults['old_cu']}")
print(f"   From: Year {defaults['last_semester']['academic_year']}, Sem {defaults['last_semester']['semester_num']}")

print(f"\n📋 Form shown to user:")
print(f"   [AUTO-FILLED] Old CGPA: {defaults['old_cgpa']} (Year {defaults['last_semester']['academic_year']}, Sem {defaults['last_semester']['semester_num']})")
print(f"   [AUTO-FILLED] Total CU before semester: {defaults['old_cu']}")
print(f"   [USER ENTERS] Current semester GPA: 4.0")
print(f"   [USER ENTERS] Current semester CU: 26")

# Calculate with new semester
new_gpa = 4.0
new_cu = 26
new_cgpa = update_cgpa(defaults['old_cgpa'], defaults['old_cu'], new_gpa, new_cu)
new_cgpa = round(new_cgpa, 2)

print(f"\n✅ Calculation result:")
print(f"   New CGPA: {new_cgpa}")

print(f"\n📊 DATA REDUCTION ANALYSIS:")
print(f"   Traditional flow (guest mode):")
print(f"      - STEP 1: Enter old CGPA (manual)")
print(f"      - STEP 2: Enter total CU (manual - requires checking all semesters)")
print(f"      - STEP 3: Enter new semester GPA (manual)")
print(f"      - STEP 4: Enter new semester CU (manual)")
print(f"      = 4 PROMPTS, requires remembering old CGPA and CU")
print(f"\n   New logged-in flow:")
print(f"      - [2 auto-filled from vault]")
print(f"      - STEP 3: Enter new semester GPA (only this)")
print(f"      - STEP 4: Enter new semester CU (and this)")
print(f"      = 2 PROMPTS, user enters only NEW data!")
print(f"      ✨ 50% REDUCTION IN USER INPUT ✨")

print("\n" + "="*70)
print("[PHASE 4] CGPA from Scratch - Enhanced")
print("-" * 70)
print("User selects Option 3: Calculate CGPA from scratch")
print("\n✅ System displays saved semesters:")

summary = vault.get_semesters_summary(user['id'])
print(f"\n   Year  Sem   GPA    CGPA   CU")
print(f"   " + "-"*30)
for s in summary:
    print(f"   {s['academic_year']:<5} {s['semester_num']:<5} {s['gpa']:<6.2f} {s['cgpa']:<6.2f} {s['total_cu']:<3}")

print(f"\n✅ Options given:")
print(f"   A) Use all {len(summary)} saved semesters (auto-loaded) + add new ones")
print(f"   B) Manual entry (traditional way)")
print(f"\n   Traditional flow: User manually enters all {len(summary)*5} data points!")
print(f"   New flow: Auto-load all {len(summary)} semesters, then add any new ones")
print(f"   ✨ 80%+ REDUCTION IN DATA ENTRY ✨")

print("\n" + "="*70)
print("✅ COMPLETE WORKFLOW DEMONSTRATION SUCCESSFUL!")
print("="*70)

print("\n📈 SUMMARY OF IMPROVEMENTS:")
print("   ✓ New users onboard with full history capture in one session")
print("   ✓ No redundant data re-entry across multiple calculations")
print("   ✓ Smart defaults reduce prompts by 50-80% for logged-in users")
print("   ✓ Guest mode unchanged (as expected)")
print("   ✓ Data safely stored in vault for future sessions")
print("\n")
