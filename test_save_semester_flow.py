#!/usr/bin/env python3
"""
Test save-semester flow end-to-end
Requires Flask server running on localhost:5000
"""
import pytest
import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000'

@pytest.mark.integration
def test_save_semester_flow():
    print("Testing save-semester flow...\n")
    
    # Step 1: Create a session (simulate login)
    session = requests.Session()
    
    # Step 2: Try to save without login (should fail)
    print("1. Testing save without login...")
    response = session.post(f'{BASE_URL}/api/save-semester', 
        json={'academic_year': 1, 'semester_num': 1, 'gpa': 3.85, 'total_cu': 15})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # Step 3: Register a test user
    print("2. Registering test user...")
    response = session.post(f'{BASE_URL}/register',
        data={'username': 'testuser999', 'password': 'pass123', 'full_name': 'Test User'},
        allow_redirects=True)
    print(f"   Status: {response.status_code}")
    print(f"   Location: {response.url}")
    print(f"   Cookies: {session.cookies.get_dict()}\n")
    
    # Step 4: Now try to save (should succeed)
    print("3. Testing save with login...")
    response = session.post(f'{BASE_URL}/api/save-semester',
        json={'academic_year': 1, 'semester_num': 1, 'gpa': 3.85, 'total_cu': 15})
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response: {data}\n")
    
    if response.status_code == 200 and 'new_cgpa' in data:
        print("[SUCCESS] Save successful!")
        print(f"   New CGPA: {data.get('new_cgpa')}")
        print(f"   Semester ID: {data.get('semester_id')}\n")
        
        # Step 5: Save another semester
        print("4. Testing save second semester...")
        response = session.post(f'{BASE_URL}/api/save-semester',
            json={'academic_year': 1, 'semester_num': 2, 'gpa': 3.90, 'total_cu': 16})
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {data}")
        
        if response.status_code == 200:
            new_cgpa = data.get('new_cgpa')
            print("[SUCCESS] Second semester saved!")
            print(f"   New CGPA after 2 semesters: {new_cgpa}")
            print(f"   Expected: (3.85*15 + 3.90*16) / 31 = ~3.88")
            expected = (3.85 * 15 + 3.90 * 16) / 31
            print(f"   Calculated: {expected:.2f}\n")
    else:
        print("[FAILED] Save failed!")

if __name__ == '__main__':
    print("=" * 60)
    print("GPA Simulator - Save Semester Test")
    print("=" * 60 + "\n")
    
    try:
        test_save_semester_flow()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
