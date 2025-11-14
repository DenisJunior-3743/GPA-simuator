# Authentication and Vault Integration Testing Guide

## Overview
The CLI now supports:
1. **User Authentication** - Register and login with password hashing
2. **Guest Mode** - Continue without saving data
3. **Authenticated Menu** - Additional options (6-10) for registered users
4. **Academic History** - View saved semesters and courses
5. **Save Semester** - Save current semester to vault with course details
6. **Logout** - Return to auth menu

## Menu Structure

### For Guests (7 options):
```
1. Calculate GPA (quick) - for current semester
2. Update CGPA - calculate CGPA after current semester
3. Calculate CGPA manually - enter all semester grades cumulatively
4. Required GPA for target CGPA - what GPA do I need next semester?
5. Simulate grade combinations - find possible grades for target GPA
6. Initialize vault database
7. Exit
```

### For Authenticated Users (10 options):
```
1. Calculate GPA (quick) - for current semester
2. Update CGPA - calculate CGPA after current semester
3. Calculate CGPA manually - enter all semester grades cumulatively
4. Required GPA for target CGPA - what GPA do I need next semester?
5. Simulate grade combinations - find possible grades for target GPA
6. View academic history
7. Save current semester to vault
8. Initialize vault database
9. Logout
10. Exit
```

## Testing Steps

### Test 1: Guest Mode
```
Input:
3
7

Expected:
- Continues as guest
- Shows guest menu (options 1-7)
- Option 6 is "Initialize vault database"
- Option 7 is "Exit"
```

### Test 2: User Registration
```
Input:
1              # Select "Register new account"
testuser       # Username
password123    # Password
John Doe       # Full name
john@test.com  # Email
Computer Science  # Program
4              # Duration (years)

Expected:
- User created successfully
- Redirects to main menu (authenticated)
- Shows options 1-10
```

### Test 3: User Login
```
Input:
2              # Select "Login"
testuser       # Username
password123    # Password

Expected:
- Login successful
- Redirects to main menu (authenticated)
- Shows options 1-10
```

### Test 4: View Academic History (Empty)
```
Input:
2              # Login
testuser
password123
6              # View academic history

Expected:
- Shows "No academic records found. Start by saving a semester."
```

### Test 5: Save Semester
```
Input:
2              # Login
testuser
password123
7              # Save current semester
1              # Academic year
1              # Semester number
2              # Number of courses
Math 101       # Course 1 name
3              # Course 1 CU
1              # Course 1 grade (A)
Physics 101    # Course 2 name
4              # Course 2 CU
2              # Course 2 grade (B+)
y              # Confirm save

Expected:
- Displays semester GPA and CGPA calculations
- Saves successfully with message
- Shows calculated GPA and cumulative CGPA
```

### Test 6: View Updated History
```
Input:
2              # Login
testuser
password123
6              # View academic history

Expected:
- Shows 1 semester saved
- Year 1, Semester 1
- 7 total CU
- Calculated GPA
- List of 2 courses with names, grades, and CU
```

### Test 7: Logout
```
Input:
2              # Login
testuser
password123
9              # Logout

Expected:
- "Logged out successfully!"
- Returns to auth menu (options 1-3)
```

## Implementation Details

### Database Schema
- **users**: username (UNIQUE), password (hashed SHA256), email, full_name, program, duration
- **semesters**: user_id (FK), academic_year, semester_num, total_cu, gpa, cgpa
- **courses**: semester_id (FK), name, credit_units, grade_letter
- **scenarios**: user_id (FK), name, params (JSON)

### Authentication
- Passwords hashed with SHA256 via `_hash_password()`
- Session managed with module-level `_current_user` variable
- Functions: `register_user()`, `login_user()`, `logout_user()`, `set_current_user()`, `get_current_user()`

### CGPA Calculation
- `calculate_current_cgpa()` - From all saved semesters
- `calculate_current_cgpa_with_new_semester()` - Preview CGPA after adding a new semester

### Menu Routing
- `is_guest = (current_user['id'] is None)` - Determines which menu to show
- Options 1-5 are same for both guest and authenticated
- Options 6-10 vary by user type
- All choice handlers check `is_guest` flag to route correctly

## Known Limitations
- Password reset not implemented
- Edit/delete semester not implemented
- Scenario saving/loading not fully implemented
- No email verification
- No password strength requirements (should add in production)

## Future Enhancements
1. Update existing semester data
2. Delete semester/course records
3. Export academic transcript
4. Share scenarios with other users
5. Password reset via email
6. Multi-user household tracking (family members)
7. GPA trends visualization
