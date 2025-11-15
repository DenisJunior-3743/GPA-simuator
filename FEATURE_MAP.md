# GPA Simulator - Complete Feature Map

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   GPA Simulator CLI                      │
└─────────────────────────────────────────────────────────┘
                          ↓
            ┌─────────────────────────────┐
            │   Authentication Layer      │
            │  (Register/Login/Guest)     │
            └─────────────────────────────┘
                    ↙          ↓          ↖
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │ Register │  │  Login   │  │  Guest   │
            │  (New)   │  │(Returning)│ │ (OneTime)│
            └──────────┘  └──────────┘  └──────────┘
                    ↓          ↓          ↓
            ┌──────────────────────────────────────┐
            │         Main Menu (Dynamic)          │
            │   Shows 7 or 10 options based on    │
            │         authentication state        │
            └──────────────────────────────────────┘
                    ↓
        ┌───────────────────────────────────┐
        │   Calculation Options (1-5)       │
        │   Available to all users:        │
        │   1. Calculate GPA               │
        │   2. Update CGPA                 │
        │   3. CGPA from scratch           │
        │   4. Required GPA                │
        │   5. Simulate grades             │
        └───────────────────────────────────┘
                    ↓
        ┌───────────────────────────────────┐
        │   User-Specific Options (6-10)    │
        │   IF Authenticated:               │
        │   6. View history                 │
        │   7. Save semester                │
        │   8. Init database                │
        │   9. Logout                       │
        │   10. Exit                        │
        │                                   │
        │   IF Guest:                       │
        │   6. Init database                │
        │   7. Exit                         │
        └───────────────────────────────────┘
                    ↓
            ┌──────────────────┐
            │ Database/Vault   │
            │ (SQLite)         │
            │ - users          │
            │ - semesters      │
            │ - courses        │
            │ - scenarios      │
            └──────────────────┘
```

## Feature Comparison Matrix

| Feature | Guest | Authenticated |
|---------|-------|---|
| Calculate GPA | ✅ | ✅ |
| Update CGPA | ✅ | ✅ |
| CGPA from scratch | ✅ | ✅ |
| Required GPA | ✅ | ✅ |
| Simulate grades | ✅ | ✅ |
| View academic history | ❌ | ✅ |
| Save semester | ❌ | ✅ |
| Initialize DB | ✅ | ✅ |
| Logout | ❌ | ✅ |
| Data persistence | ❌ | ✅ |
| Course naming | ❌ | ✅ |
| Multi-semester tracking | ❌ | ✅ |

## Data Flow Diagram

### User Registration Flow
```
User Input
  ├─ Username (checked for uniqueness)
  ├─ Password (hashed with SHA256)
  ├─ Full Name
  ├─ Email
  ├─ Program
  └─ Duration (years)
        ↓
   [vault_manager.py]
   register_user()
        ↓
   INSERT INTO users
        ↓
   Set current_user in memory
        ↓
   Redirect to Main Menu (Authenticated)
```

### Save Semester Flow
```
User Input (Option 7)
  ├─ Academic year (1-5)
  ├─ Semester number (1-2)
  └─ For each course:
      ├─ Course name
      ├─ Credit units
      └─ Grade (numeric 1-8)
        ↓
   Calculate GPA from grades
        ↓
   Calculate CGPA including past semesters
        ↓
   Display preview to user
        ↓
   Confirm save (y/n)
        ↓
   INSERT INTO semesters
        ↓
   INSERT INTO courses (one per course)
        ↓
   Success message
```

### View History Flow
```
Select Option 6
        ↓
   SELECT FROM semesters
   WHERE user_id = ?
   ORDER BY academic_year, semester_num
        ↓
   For each semester:
      SELECT FROM courses
      WHERE semester_id = ?
        ↓
   Format and display:
      Year X, Semester Y
      Total CU: Z
      Semester GPA: W
      CGPA: V
      Courses:
        - Name1: Grade1 (CU1)
        - Name2: Grade2 (CU2)
```

## Database Schema Details

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,    -- e.g., "john_doe_2024"
    password TEXT NOT NULL,            -- SHA256 hashed
    email TEXT,                        -- e.g., "john@university.edu"
    full_name TEXT,                    -- e.g., "John Smith"
    program TEXT,                      -- e.g., "Computer Science"
    duration INTEGER,                  -- e.g., 4 (years)
    created_at TIMESTAMP
)

CREATE TABLE semesters (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL FK,       -- Link to user
    academic_year INTEGER,             -- 1, 2, 3, 4, 5
    semester_num INTEGER,              -- 1 or 2
    total_cu INTEGER,                  -- Sum of all course CUs
    gpa REAL,                          -- Semester GPA (0-5.0)
    cgpa REAL,                         -- Cumulative GPA after this semester
    created_at TIMESTAMP
)

CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    semester_id INTEGER NOT NULL FK,   -- Link to semester
    name TEXT,                         -- e.g., "Calculus I"
    credit_units INTEGER,              -- e.g., 4
    grade_letter TEXT                  -- A, B+, B, etc.
)

CREATE TABLE scenarios (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL FK,       -- Link to user
    name TEXT,                         -- e.g., "If I get all A's"
    params TEXT                        -- JSON string
)
```

## Calculation Formulas

### Semester GPA
```
Semester GPA = (Grade1_Points × CU1 + Grade2_Points × CU2 + ...) / Total_CU

Example:
  A (5.0) × 4 CU = 20
  B+ (4.5) × 3 CU = 13.5
  B (4.0) × 3 CU = 12
  Total = 45.5 / 10 CU = 4.55
```

### Cumulative CGPA
```
CGPA = (Sem1_GPA × Sem1_CU + Sem2_GPA × Sem2_CU + ...) / Total_All_CU

Example:
  Year 1 Sem 1: GPA 4.0, CU 14
  Year 1 Sem 2: GPA 3.9, CU 14
  CGPA = (4.0×14 + 3.9×14) / 28 = 3.95
```

### CGPA with New Semester (Preview)
```
New_CGPA = (Current_CGPA × Current_CU + New_GPA × New_CU) / (Current_CU + New_CU)

Example:
  Current CGPA: 3.8, CU: 28
  New semester: GPA 4.1, CU 14
  Preview = (3.8×28 + 4.1×14) / 42 = 3.92
```

## Grade Point Scale

| Grade | Points |
|-------|--------|
| A | 5.0 |
| B+ | 4.5 |
| B | 4.0 |
| C+ | 3.5 |
| C | 3.0 |
| D+ | 2.5 |
| D | 2.0 |
| F | 0.0 |

## Workflow Examples

### Example 1: New Student
```
TIME: First interaction
  → Select "Register" (Option 1)
  → Create account: @jsmith, password, ...
  → Logged in → Main Menu (10 options)
  → Select "Save semester" (Option 7)
  → Enter: Year 1, Semester 1, 4 courses
  → System saves data
  → CGPA = 3.8 (first semester, no cumulative)

TIME: Next semester
  → Run CLI
  → Select "Login" (Option 2)
  → Enter: @jsmith, password
  → Logged in → Main Menu (10 options)
  → Select "Save semester" (Option 7)
  → Enter: Year 1, Semester 2, 4 courses
  → System calculates CGPA including both semesters
  → CGPA = (3.8 × 14 + 3.9 × 14) / 28 = 3.85

TIME: End of year review
  → Select "View history" (Option 6)
  → Shows both semesters
  → CGPA progression: 3.8 → 3.85
```

### Example 2: Guest User Planning
```
TIME: Studying for exams
  → Select "Continue as guest" (Option 3)
  → Not logged in → Main Menu (7 options)
  → Select "Simulate grades" (Option 5)
  → Enter: Target GPA 4.0, 5 courses, 15 CU total
  → System shows: Get A's in 2 courses, B+ in 3 courses
  → Exit
  → No data saved
  
TIME: Later
  → Run CLI again
  → Select "Login"
  → Same calculation would show in history
```

### Example 3: Required GPA Calculation
```
SCENARIO: Junior looking ahead
  Input:
    Old CGPA: 3.75
    Total CU completed: 42
    Upcoming semester CU: 15
    Target CGPA: 3.85
    
  Calculation:
    3.85 = (3.75 × 42 + X × 15) / 57
    3.85 × 57 = 157.5 + 15X
    219.45 = 157.5 + 15X
    X = 4.13
    
  Result:
    "You need GPA 4.13 next semester to reach 3.85 CGPA"
```

## State Diagram

```
┌─────────────────┐
│   Startup       │
│ (No Auth)       │
└────────┬────────┘
         │
         ├─ Register ──→ ┌──────────────────┐
         │               │ Create Account   │
         │               │ Hash Password    │
         │               │ Set current_user │
         │               └────────┬─────────┘
         │                        │
         ├─ Login ───────→ ┌──────────────────┐
         │                 │ Verify Creds     │
         │                 │ Set current_user │
         │                 └────────┬─────────┘
         │                          │
         └─ Guest ─────→ ┌──────────────────┐
                         │ Skip Auth        │
                         │ is_guest = True  │
                         └────────┬─────────┘
                                  │
                         ┌────────▼─────────┐
                         │  Main Menu       │
                         │(show options)    │
                         └────────┬─────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
    ┌───▼────┐  ┌────────────┐  ┌─▼────────┐    ┌────────┐
    │Calc    │  │Save        │  │View      │    │Logout  │
    │Options │  │Semester    │  │History   │    │(Auth   │
    │(1-5)   │  │(Auth 7)    │  │(Auth 6)  │    │only)   │
    └────────┘  └────────────┘  └──────────┘    └───┬────┘
                                                     │
                                            Back to Auth
```

## Success Metrics

✅ All features implemented
✅ All users can access calculations (1-5)
✅ Authenticated users can save and view history
✅ Guest users have no storage burden
✅ Database properly stores and retrieves data
✅ CGPA correctly calculated from multiple semesters
✅ Menu routing works based on authentication state
✅ Error handling for all edge cases
✅ Windows compatibility verified
✅ Cross-platform ready

## Summary

The GPA Simulator now provides:
- **For Students**: Track academic progress with persistent storage
- **For Advisors**: View complete academic history and CGPA trends
- **For One-Time Users**: Quick calculations without account hassle
- **For All**: Accurate GPA/CGPA calculations and what-if scenarios

System is complete, tested, and ready for deployment.
