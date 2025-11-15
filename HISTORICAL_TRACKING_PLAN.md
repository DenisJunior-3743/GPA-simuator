# Historical Academic Records Tracking Plan

## Problem Statement
Currently, the system requires users to manually re-enter all their historical data every time they want to:
- Calculate CGPA from scratch (Menu Option 3)
- Calculate required GPA for target (Menu Option 4)
- View academic history

This creates redundancy where logged-in users experience the same repetitive data entry as guest mode.

## Solution: Smart Historical Tracking System

### Core Concept
Capture and auto-populate historical data at natural workflow points where users are already entering data for calculations or simulations.

---

## Proposed Workflow Architecture

### Phase 1: Year/Semester Registration (New User Onboarding)
**When:** First login or early in session  
**What to capture:** User's cumulative academic history structure

```
After successful login:
├─ Check if user has any saved semesters
├─ If YES → Skip to current semester entry
└─ If NO → Offer year/semester history registration:
    ├─ "It looks like this is your first time. Let's set up your academic history."
    ├─ "What year are you in?" (1-5)
    ├─ "How many COMPLETED semesters?" (0-10)
    └─ For each completed semester:
        ├─ Academic year and semester number
        ├─ CGPA at end of that semester
        ├─ Total CU completed up to that semester
        └─ [Optional] Detailed courses for that semester
```

**Storage:** Create initial semester records in vault

---

### Phase 2: Intelligent Auto-Population During Calculations

#### When Option 2 (Update CGPA) is used:
```
Current Flow:
├─ Ask: Enter old CGPA
├─ Ask: Enter total CU before semester
├─ Ask: Enter current semester GPA
├─ Ask: Enter current semester CU

NEW Flow:
├─ Check vault for last saved semester
├─ If found:
│   ├─ Pre-populate: "Your last recorded CGPA was {X} (Year {Y}, Sem {Z})"
│   ├─ Auto-fill: Old CGPA and Old CU from last semester
│   ├─ User can accept (press Enter) or edit
│   └─ Then ask for NEW semester GPA and CU only
└─ If not found:
    └─ Fall back to manual entry (current behavior)
```

**Benefit:** From 4 prompts → 2 prompts for subsequent semesters

---

#### When Option 3 (Calculate CGPA from scratch) is used:
```
Current Flow:
├─ Ask for each semester individually:
│   ├─ Academic year
│   ├─ Semester number
│   ├─ Each course in semester
│   │   ├─ Course name
│   │   ├─ Credit units
│   │   └─ Grade
│   └─ Repeat for all semesters

NEW Flow:
├─ Check vault for saved semesters
├─ Display: "Found X completed semesters in your vault"
├─ Option A: Use saved semesters (load auto)
│   ├─ Display all saved semesters with their GPAs
│   ├─ User selects which ones to include in CGPA calc
│   └─ Add any NEW unsaved semesters manually if needed
└─ Option B: Manual entry (current behavior)
```

**Benefit:** For a Year 3 student, potentially goes from 15+ prompts → 2-3 prompts

---

#### When Option 4 (Required GPA for target) is used:
```
Current Flow:
├─ Ask: Enter old CGPA
├─ Ask: Enter total CU before semester
├─ Ask: Enter upcoming semester CU
├─ Ask: Enter target CGPA

NEW Flow:
├─ Auto-detect from vault:
│   ├─ Old CGPA (from last semester)
│   ├─ Old CU (sum of all completed semesters)
├─ User confirms or edits these values
├─ Ask only for:
│   ├─ Upcoming semester CU
│   └─ Target CGPA
└─ Show calculation
```

**Benefit:** From 4 prompts → 1-2 new prompts (2 auto-filled)

---

### Phase 3: Post-Calculation Capture

**After ANY calculation** (GPA, CGPA, Simulator):
```
[CALCULATION COMPLETED]
├─ Display result
├─ Prompt: "Would you like to save this {semester/scenario} to your vault?"
│   ├─ YES: Collect minimal info if not already entered
│   │   ├─ If it's a new semester, ask only:
│   │   │   ├─ Academic year
│   │   │   └─ Semester number
│   │   └─ (courses and GPA already entered)
│   └─ NO: Continue to menu
└─ If saved → Show confirmation with previous CGPA vs new CGPA
```

---

### Phase 4: Persistent Session Context

**During a session**, store in memory:
```python
session_context = {
    "user_id": current_user['id'],
    "current_year": 3,
    "current_semester": 1,
    "last_calculated_gpa": 4.0,
    "last_calculated_cgpa": 3.95,
    "last_entry_type": "calculation",  # or "manual_entry" or "saved"
    "current_entry_courses": [...],    # courses being entered THIS session
}
```

This allows:
- Pre-filling subsequent calculations with "last used" values
- Suggesting: "Continue with Year 3, Semester 1?" 
- Not re-asking for year/semester if user does multiple calcs in same session

---

## Data Model Additions

### Existing Schema (Already in vault_manager.py):
```
users → semesters → courses
users → scenarios
```

### New Capabilities Needed:
1. **Query: Get last completed semester for a user**
   ```python
   def get_latest_semester(user_id) → semester_dict
   ```
   ✅ Already exists in vault_manager.py

2. **Query: Get all semesters as summary**
   ```python
   def get_semesters_summary(user_id) → [
       {year: 3, sem: 1, gpa: 4.0, cgpa: 3.95, cu: 27, course_count: 7},
       ...
   ]
   ```
   ⏳ Need to add

3. **Command: Get total CU completed**
   ```python
   def get_total_cu_completed(user_id) → int
   ```
   ⏳ Need to add

---

## Menu Flow Changes

### For Logged-In Users (vs Guest):

**BEFORE** (Current):
```
Option 1: Calculate GPA → enter courses (4-8 prompts)
Option 2: Update CGPA → 4 prompts
Option 3: Calculate CGPA from scratch → 10-20+ prompts
Option 4: Required GPA → 4 prompts
Option 5: Simulate → configure and calculate
Option 6: View academic history → show saved data
Option 7: Save semester → 3 prompts
```

**AFTER** (Proposed):
```
Option 1: Calculate GPA → same (course entry)
Option 2: Update CGPA → 2 prompts (auto-fill old data)
Option 3: Calculate CGPA from scratch → 2 prompts (select from vault)
Option 4: Required GPA → 1-2 prompts (auto-fill old data)
Option 5: Simulate → same (but suggest year/sem from context)
Option 6: View academic history → same (enhanced display)
Option 7: Save semester → 2 prompts (year/sem), optional if already saving
```

---

## Implementation Roadmap

### Stage 1: Foundation (Week 1)
- [ ] Add helper functions to vault_manager.py:
  - `get_semesters_summary(user_id)`
  - `get_total_cu_completed(user_id)`
  - `get_last_complete_semester_data(user_id)`

- [ ] Create session context manager (in main.py or new module):
  - Store current year/semester/last values
  - Methods to update/retrieve

### Stage 2: Auto-Population (Week 2)
- [ ] Modify Option 2 flow to auto-fill old CGPA/CU
- [ ] Modify Option 3 flow to offer vault data loading
- [ ] Modify Option 4 flow to auto-fill old CGPA/CU

### Stage 3: Post-Calculation Capture (Week 3)
- [ ] After each calculation, offer immediate save
- [ ] Refactor calculations to return metadata for capture

### Stage 4: Testing & Polish (Week 4)
- [ ] Test with multi-year data
- [ ] UI/UX refinement
- [ ] Edge case handling

---

## Benefits

| User Type | Before | After | Reduction |
|-----------|--------|-------|-----------|
| Guest | 4-8 prompts per calc | Same | 0% |
| Logged-in (Semester 1) | 4-8 prompts per calc | 2-3 prompts | ~50% |
| Logged-in (Year 3, Sem 1) | 10-20+ prompts for CGPA calc | 2-3 prompts | ~85% |
| **Repeat sessions** | Same repetition | **Only 1 prompt** | **~95%** |

---

## Edge Cases to Handle

1. **New user (no history)**
   - Offer optional first-time setup
   - Fall back to manual entry if skipped

2. **User with gaps (e.g., took break)**
   - Allow flexible year/semester entry
   - Don't force continuity

3. **User wants to recalculate history**
   - Option to override/edit saved semester
   - Recalculate CGPA chain

4. **Switching between Year 3, Sem 1 and Year 3, Sem 2**
   - Remember last used year/sem in session
   - Suggest it as default

5. **Partial entry (user closes mid-entry)**
   - Session context cleared on logout
   - No unsaved partial data persists

---

## Success Metrics

✅ Logged-in users reduce data entry by 50-95% on repeat calculations  
✅ Natural, guided onboarding for new users  
✅ All historical data safely stored and retrievable  
✅ No forced "history setup" - optional but recommended  
✅ Seamless UX difference between guest and logged-in modes  

