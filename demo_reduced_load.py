#!/usr/bin/env python3
"""
Interactive demo showing the reduced-load workflow.

This script demonstrates what a user experiences with the new system:
1. Registration with onboarding
2. Option 2 with smart defaults
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import vault_manager as vault
from main import get_smart_defaults_from_vault
from app.cgpa_calculator import update_cgpa

vault.init_db()

print("\n" + "="*70)
print("INTERACTIVE DEMO: User Experience with Reduced Load System")
print("="*70)

print("\n[1] NEW USER REGISTRATION")
print("-"*70)
print("Scenario: New student registering for the first time\n")

user = vault.register_user(
    'demo_student',
    'password123',
    'Demo Student',
    'demo@university.edu',
    'Engineering',
    4
)

print(f"✅ Registration successful!")
print(f"   Username: {user['username']}")
print(f"   Name: {user['full_name']}")
print(f"   Program: {user['program']}")

print("\n[2] ONBOARDING FLOW (Simulated)")
print("-"*70)
print("System: 'Welcome! Let's set up your academic history.'")
print("System: 'You can save time later by setting this up now.'")
print("User: 'Yes, let's do it'\n")

print("System: 'What year are you currently in? (1-5)'")
print("User: '3'")
print("System: 'What semester in year 3? (1 or 2)'")
print("User: '1'\n")

print("System: 'Quick entry (CU+GPA only) or Detailed (with courses)?'")
print("User: 'Quick - I'm in a hurry'\n")

print("System: 'Enter your 5 completed semesters...'")
semesters_data = [
    (1, 1, 24, 3.4, "Year 1, Semester 1"),
    (1, 2, 24, 3.5, "Year 1, Semester 2"),
    (2, 1, 25, 3.6, "Year 2, Semester 1"),
    (2, 2, 25, 3.7, "Year 2, Semester 2"),
    (3, 1, 26, 3.8, "Year 3, Semester 1 (current)"),
]

cumulative_cgpa = 0
cumulative_cu = 0

for y, s, cu, gpa, label in semesters_data:
    if y == 1 and s == 1:
        cumulative_cgpa = gpa
    else:
        cumulative_cgpa = vault.calculate_current_cgpa_with_new_semester(user['id'], gpa, cu)
        cumulative_cgpa = round(cumulative_cgpa, 2)
    
    cumulative_cu += cu
    vault.save_semester(user['id'], y, s, cu, gpa, cumulative_cgpa, [])
    print(f"  User enters {label}: CU={cu}, GPA={gpa}")

print(f"\nSystem: 'Save this? (Review below)'")
print(f"\n   Year  Sem   GPA    CGPA   CU")
for s in vault.get_semesters_summary(user['id']):
    print(f"   {s['academic_year']:<5} {s['semester_num']:<5} {s['gpa']:<6.2f} {s['cgpa']:<6.2f} {s['total_cu']:<3}")

print(f"\nUser: 'Yes, save it'")
print(f"✅ 5 semesters saved to vault!")

print("\n" + "="*70)
print("[3] LATER SESSION: User calculates new CGPA (Option 2)")
print("="*70)
print("Scenario: User completes Year 3, Semester 2 and calculates new CGPA\n")

print("User logs in...")
user = vault.login_user('demo_student', 'password123')
print(f"✅ Welcome back, {user['full_name']}!\n")

print("User selects: Option 2 - Update CGPA\n")

# Get smart defaults
defaults = get_smart_defaults_from_vault(user['id'])

print("System automatically retrieves:")
print(f"  ✅ Last recorded CGPA: {defaults['old_cgpa']}")
print(f"  ✅ Total CU completed: {defaults['old_cu']}")
print(f"  ✅ From: Year {defaults['last_semester']['academic_year']}, Sem {defaults['last_semester']['semester_num']}\n")

print("FORM DISPLAY:")
print("┌─────────────────────────────────────┐")
print(f"│ Step 1: Old CGPA (from vault)       │")
print(f"│ [AUTO-FILLED] {defaults['old_cgpa']}                        │")
print(f"│ (Year {defaults['last_semester']['academic_year']}, Semester {defaults['last_semester']['semester_num']} - press Enter to accept)  │")
print("├─────────────────────────────────────┤")
print(f"│ Step 2: Total CU before new sem     │")
print(f"│ [AUTO-FILLED] {defaults['old_cu']}                        │")
print(f"│ (press Enter to accept)              │")
print("├─────────────────────────────────────┤")
print("│ Step 3: Current semester GPA        │")
print("│ [USER ENTERS] 3.9                   │")
print("├─────────────────────────────────────┤")
print("│ Step 4: Current semester CU         │")
print("│ [USER ENTERS] 26                    │")
print("└─────────────────────────────────────┘\n")

print("User presses Enter 2x to accept defaults, then enters 3.9 and 26\n")

# Calculate
new_cgpa = update_cgpa(defaults['old_cgpa'], defaults['old_cu'], 3.9, 26)
new_cgpa = round(new_cgpa, 2)

print("✅ RESULT:")
print(f"   New CGPA: {new_cgpa}")
print(f"   Previous CGPA: {defaults['old_cgpa']}")
print(f"   Improvement: {new_cgpa - defaults['old_cgpa']:.2f}\n")

print("System: 'Save this semester to vault? (y/n)'")
print("User: 'y'")

vault.save_semester(user['id'], 3, 2, 26, 3.9, new_cgpa, [])
print("✅ Semester saved!\n")

print("="*70)
print("[COMPARISON] Traditional vs New Flow")
print("="*70)

print("\n🔴 TRADITIONAL FLOW (Guest Mode):")
print("   Step 1: \"Enter your old CGPA: \" → User manually looks it up → enters manually")
print("   Step 2: \"Enter total CU before:\" → User adds up all semesters → enters manually")
print("   Step 3: \"Enter current GPA: \"   → User enters 3.9")
print("   Step 4: \"Enter current CU: \"    → User enters 26")
print("   = 4 MANUAL INPUTS, requires remembering/calculating")

print("\n🟢 NEW FLOW (Logged-in with onboarding):")
print("   Step 1: [AUTO-FILLED] 3.68 (press Enter to accept)")
print("   Step 2: [AUTO-FILLED] 124 (press Enter to accept)")
print("   Step 3: \"Enter current GPA: \"   → User enters 3.9")
print("   Step 4: \"Enter current CU: \"    → User enters 26")
print("   = 2 MANUAL INPUTS + 2 ENTER PRESSES = 50% LESS WORK!")

print("\n" + "="*70)
print("✅ DEMO COMPLETE")
print("="*70)
print("\n📊 Key Takeaways:")
print("   ✓ First-time setup: One onboarding saves future repetition")
print("   ✓ Smart defaults: Old CGPA and CU auto-filled from vault")
print("   ✓ User only enters: New semester GPA and CU")
print("   ✓ Result: 50% fewer prompts, no mental math needed")
print("   ✓ Data safety: Everything stored for future use")
print("\n")
