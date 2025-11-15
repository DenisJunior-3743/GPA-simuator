"""Main CLI for offline GPA & CGPA Simulator.
Usage:
    python main.py --cli      # interactive CLI
    python main.py --init-db  # initialize sqlite vault
"""
import argparse
from app.gpa_calculator import compute_gpa
from app.cgpa_calculator import update_cgpa, required_gpa_for_target
from app.simulator import generate_grade_combinations
from app import vault_manager as vault
from app.session_context import get_session, reset_session
from app.onboarding import onboard_first_time_user
from app.constants import GRADE_POINTS

MAX_GPA = 5.0
DECIMAL_PLACES = 2

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_instruction(text: str):
    """Print an instruction in a highlighted format."""
    print(f"\n[INSTRUCTION] {text}")

def print_warning(text: str):
    """Print a warning message."""
    print(f"\n[WARNING] {text}")

def print_info(text: str):
    """Print info message."""
    print(f"\n[INFO] {text}")

def print_success(text: str):
    """Print success message."""
    print(f"\n[SUCCESS] {text}")

def display_grade_menu():
    """Display available grades and their corresponding numbers."""
    grades = list(GRADE_POINTS.keys())
    print('\nAvailable grades:')
    for i, grade in enumerate(grades, 1):
        print(f'  {i}. {grade}')
    return grades

def prompt_grade(course_num: int) -> str:
    """Prompt user to select a grade by number."""
    grades = display_grade_menu()
    while True:
        try:
            choice = input(f"Course {course_num} grade (enter number 1-{len(grades)}): ").strip()
            if not choice.isdigit():
                print_warning(f'Please enter a number between 1 and {len(grades)}.')
                continue
            choice_int = int(choice)
            if choice_int < 1 or choice_int > len(grades):
                print_warning(f'Please enter a number between 1 and {len(grades)}.')
                continue
            return grades[choice_int - 1]
        except Exception as e:
            print_warning(f'Error: {e}')

def validate_gpa(gpa: float, label: str = "GPA") -> bool:
    """Validate that GPA does not exceed maximum."""
    if gpa > MAX_GPA:
        print_warning(f'{label} cannot exceed {MAX_GPA}. You entered {gpa}.')
        print_instruction(f'Please check your input values and try again.')
        return False
    return True

def prompt_positive_float(prompt_text: str, label: str = "Value", max_val: float = None) -> float:
    """Prompt user for a positive float value with validation."""
    while True:
        try:
            value = float(input(prompt_text).strip())
            if value < 0:
                print_warning(f'{label} must be positive. You entered {value}.')
                continue
            if max_val is not None and value > max_val:
                print_warning(f'{label} cannot exceed {max_val}. You entered {value}.')
                continue
            return value
        except ValueError:
            print_warning(f'Please enter a valid number.')

def prompt_positive_int(prompt_text: str, label: str = "Value", max_val: int = None) -> int:
    """Prompt user for a positive integer value with validation.

    Args:
        prompt_text: text shown to the user
        label: friendly label used in warnings
        max_val: optional maximum allowed value (inclusive)
    """
    while True:
        try:
            value = int(input(prompt_text).strip())
            if value <= 0:
                print_warning(f'{label} must be positive. You entered {value}.')
                continue
            if max_val is not None and value > max_val:
                print_warning(f'{label} cannot exceed {max_val}. You entered {value}.')
                continue
            return value
        except ValueError:
            print_warning(f'Please enter a valid number.')

def calculate_total_cu_helper() -> int:
    """Helper to calculate total CU by asking for semesters or letting user input directly."""
    print_instruction('You can calculate your total CU in two ways:')
    print('  1. Enter total CU directly (if you know the sum)')
    print('  2. Enter CU per semester (we will sum them up for you)')
    
    while True:
        choice = input('\nChoose option (1 or 2): ').strip()
        if choice == '1':
            print_instruction('Please check your curriculum for all Credit Units (CU) you completed.')
            print_info('CU per course is usually found in your course syllabus or course catalog.')
            cu = prompt_positive_int('Enter total credit units completed: ', 'Total CU')
            return cu
        elif choice == '2':
            print_instruction('We will calculate your total CU by semester.')
            print_info('We will ask for CU from semester 1 of year 1 up to your CURRENT semester.')
            
            current_year = prompt_positive_int('What is your current academic year? (e.g., 1, 2, 3, 4, 5): ', 'Current year', max_val=5)
            current_sem = prompt_positive_int('What is your current semester in year {y}? (1 or 2): '.format(y=current_year), 'Current semester')
            
            # Validate semester input
            while current_sem not in (1, 2):
                print_warning('Semester must be 1 or 2.')
                current_sem = prompt_positive_int('What is your current semester? (1 or 2): ', 'Current semester')
            
            total_cu = 0
            # Calculate total semesters completed (semesters BEFORE current one)
            completed_semesters = (current_year - 1) * 2 + (current_sem - 1)
            
            if completed_semesters == 0:
                print_info('You have no completed semesters yet.')
                return 0
            
            print_success(f'You have {completed_semesters} completed semester(s).')
            
            # Iterate through all completed semesters
            semester_count = 0
            for year_num in range(1, current_year + 1):
                for sem_num in range(1, 3):
                    semester_count += 1
                    # Stop at current semester (only count completed ones)
                    if year_num == current_year and sem_num == current_sem:
                        break
                    
                    print(f'\n--- Year {year_num}, Semester {sem_num} ---')
                    print_instruction('Please check your curriculum for CU per course in this semester.')
                    
                    # Display clear options
                    print('\nHow would you like to enter CU for this semester?')
                    print('  1. Enter CU per course (we will sum them)')
                    print('  2. Enter total CU for semester directly')
                    
                    # Ask if they want to enter per-course CU or semester total
                    while True:
                        sub_choice = input('\nSelect option (1 or 2): ').strip()
                        if sub_choice == '1':
                            n_courses = prompt_positive_int(f'How many courses in Year {year_num}, Semester {sem_num}? ', 'Number of courses')
                            sem_cu = 0
                            for course_num in range(1, n_courses + 1):
                                cu_val = prompt_positive_int(f'  Course {course_num} CU: ', 'CU')
                                sem_cu += cu_val
                            print_success(f'Year {year_num}, Semester {sem_num} total CU: {sem_cu}')
                            total_cu += sem_cu
                            break
                        elif sub_choice == '2':
                            sem_cu = prompt_positive_int(f'Enter total CU for Year {year_num}, Semester {sem_num}: ', 'Semester CU')
                            print_success(f'Year {year_num}, Semester {sem_num} total CU: {sem_cu}')
                            total_cu += sem_cu
                            break
                        else:
                            print_warning('Please enter 1 or 2.')
                
                # Break outer loop if we reached current semester
                if year_num == current_year and current_sem == 1:
                    break
            
            print_success(f'Total CU calculated: {total_cu}')
            return total_cu
        else:
            print_warning('Please enter 1 or 2.')

def calculate_cgpa_from_scratch() -> float:
    """Calculate CGPA by entering semester GPA and CU for all completed semesters."""
    print_instruction('You will enter your GPA and CU for each semester up to and including your current semester.')
    print_info('Start from Year 1, Semester 1 and continue to your current semester.')
    
    current_year = prompt_positive_int('What is your current academic year? (e.g., 1, 2, 3, 4, 5): ', 'Current year', max_val=5)
    current_sem = prompt_positive_int('What is your current semester in year {y}? (1 or 2): '.format(y=current_year), 'Current semester')
    
    # Validate semester input
    while current_sem not in (1, 2):
        print_warning('Semester must be 1 or 2.')
        current_sem = prompt_positive_int('What is your current semester? (1 or 2): ', 'Current semester')
    
    total_gpa_weighted = 0.0
    total_cu = 0
    semester_count = 0
    
    # Calculate total semesters to include (up to and including current semester)
    total_semesters = (current_year - 1) * 2 + current_sem
    
    if total_semesters == 0:
        print_info('You have no semesters to enter.')
        return 0.0
    
    print_success(f'You will enter GPA and CU for {total_semesters} semester(s).')
    
    # Iterate through all semesters up to and including current semester
    for year_num in range(1, current_year + 1):
        for sem_num in range(1, 3):
            semester_count += 1
            # Stop after current semester
            if year_num == current_year and sem_num == current_sem:
                pass  # Include this semester
            elif year_num == current_year and sem_num > current_sem:
                break  # Stop if we go beyond current semester
            
            print(f'\n--- Year {year_num}, Semester {sem_num} ---')
            print_instruction('Please check your academic record for this semester\'s GPA and total credit units.')
            
            # Get semester GPA
            sem_gpa = prompt_positive_float(f'Enter GPA for Year {year_num}, Semester {sem_num} (0.0 - 5.0): ', 
                                           f'Semester {sem_num} GPA', MAX_GPA)
            
            # Get semester CU
            print('\nHow would you like to enter CU for this semester?')
            print('  1. Enter CU per course (we will sum them)')
            print('  2. Enter total CU for semester directly')
            
            while True:
                sub_choice = input('\nSelect option (1 or 2): ').strip()
                if sub_choice == '1':
                    n_courses = prompt_positive_int(f'How many courses in Year {year_num}, Semester {sem_num}? ', 'Number of courses')
                    sem_cu = 0
                    for course_num in range(1, n_courses + 1):
                        cu_val = prompt_positive_int(f'  Course {course_num} CU: ', 'CU')
                        sem_cu += cu_val
                    print_success(f'Year {year_num}, Semester {sem_num} total CU: {sem_cu}')
                    break
                elif sub_choice == '2':
                    sem_cu = prompt_positive_int(f'Enter total CU for Year {year_num}, Semester {sem_num}: ', 'Semester CU')
                    print_success(f'Year {year_num}, Semester {sem_num} total CU: {sem_cu}')
                    break
                else:
                    print_warning('Please enter 1 or 2.')
            
            # Add to cumulative calculation
            total_gpa_weighted += sem_gpa * sem_cu
            total_cu += sem_cu
            
            # Display running CGPA
            running_cgpa = total_gpa_weighted / total_cu if total_cu > 0 else 0.0
            running_cgpa = round(running_cgpa, DECIMAL_PLACES)
            print_info(f'Running CGPA after {semester_count} semester(s): {running_cgpa}')
            
            # Stop if we've reached the current semester
            if year_num == current_year and sem_num == current_sem:
                break
        
        # Break outer loop if we reached current semester
        if year_num == current_year:
            break
    
    # Calculate final CGPA
    final_cgpa = total_gpa_weighted / total_cu if total_cu > 0 else 0.0
    final_cgpa = round(final_cgpa, DECIMAL_PLACES)
    
    print_success(f'\nFinal CGPA based on {total_semesters} semester(s): {final_cgpa}')
    return final_cgpa


def get_smart_defaults_from_vault(user_id: int) -> dict:
    """Get old CGPA and old CU from vault for auto-population in calculations.
    
    Returns dict: {
        'old_cgpa': float or None,
        'old_cu': int or None,
        'last_semester': dict or None  # {academic_year, semester_num, gpa, cgpa, total_cu}
    }
    """
    result = {
        'old_cgpa': None,
        'old_cu': None,
        'last_semester': None
    }
    
    try:
        last = vault.get_last_complete_semester_data(user_id)
        if last:
            result['last_semester'] = {
                'academic_year': last['academic_year'],
                'semester_num': last['semester_num'],
                'gpa': last['gpa'],
                'cgpa': last['cgpa'],
                'total_cu': last['total_cu']
            }
            # After completing the last semester, that semester's CGPA becomes the old CGPA
            result['old_cgpa'] = last['cgpa']
            # And total CU so far includes that last semester
            result['old_cu'] = vault.get_total_cu_completed(user_id)
    except Exception:
        pass  # If vault queries fail, return empty defaults
    
    return result


def prompt_update_cgpa_with_defaults(user_id: int) -> tuple:
    """Prompt for Update CGPA with smart defaults from vault.
    
    Returns: (old_cgpa, old_cu, new_gpa, new_cu)
    """
    defaults = get_smart_defaults_from_vault(user_id)
    
    print_instruction('STEP 1: Enter your OLD CGPA (before current semester)')
    
    # If we have a default, show it
    if defaults['old_cgpa'] is not None:
        print_info(f'Last recorded CGPA: {defaults["old_cgpa"]} (Year {defaults["last_semester"]["academic_year"]}, Sem {defaults["last_semester"]["semester_num"]})')
        suggest = input('Use this value? (press Enter for yes, or type new value): ').strip()
        if suggest:
            old_cgpa = float(suggest)
        else:
            old_cgpa = defaults['old_cgpa']
    else:
        print_info('No previous semesters found. Please enter your old CGPA manually.')
        old_cgpa = prompt_positive_float('Enter old CGPA (0.0 - 5.0): ', 'Old CGPA', MAX_GPA)
    
    print_instruction('STEP 2: Enter total credit units completed BEFORE current semester')
    if defaults['old_cu'] is not None:
        print_info(f'Total CU completed so far: {defaults["old_cu"]}')
        suggest = input('Use this value? (press Enter for yes, or type new value): ').strip()
        if suggest:
            old_cu = int(suggest)
        else:
            old_cu = defaults['old_cu']
    else:
        old_cu = calculate_total_cu_helper()
    
    print_instruction('STEP 3: Enter your CURRENT SEMESTER GPA')
    print_info('This is the GPA you calculated for your most recent semester.')
    new_gpa = prompt_positive_float('Enter current semester GPA (0.0 - 5.0): ', 'Current GPA', MAX_GPA)
    
    print_instruction('STEP 4: Enter credit units for CURRENT SEMESTER')
    new_cu = prompt_positive_int('Enter current semester credit units: ', 'Current semester CU')
    
    # Store in session context for later use
    session = get_session()
    session.set_last_calculation(gpa=new_gpa, cgpa=None, cu=new_cu, entry_type="manual_entry")
    
    return (old_cgpa, old_cu, new_gpa, new_cu)


def calculate_cgpa_from_scratch_with_vault(user_id: int) -> float:
    """Calculate CGPA - loads from vault if available, else manual entry."""
    saved = vault.get_semesters_for_user(user_id)
    if saved and len(saved) > 0:
        summary = vault.get_semesters_summary(user_id)
        print_instruction('We found saved semesters in your vault!')
        print(f'\n✅ Your saved semesters ({len(summary)} total):')
        print(f'{"Year":<6} {"Sem":<5} {"GPA":<8} {"CGPA":<8} {"CU":<8}')
        print('-' * 35)
        for s in summary:
            print(f'{s["academic_year"]:<6} {s["semester_num"]:<5} {s["gpa"]:<8.2f} {s["cgpa"]:<8.2f} {s["total_cu"]:<8}')
        print_instruction('Would you like to:')
        print('  1. Use all saved semesters (add new ones if needed)')
        print('  2. Start fresh - enter all semesters manually')
        while True:
            c = input('\nSelect (1 or 2): ').strip()
            if c == '1':
                wt, cu = 0.0, 0
                for s in saved:
                    wt += s['gpa'] * s['total_cu']
                    cu += s['total_cu']
                print_success(f'✅ Loaded {len(saved)} semester(s) from vault')
                if input('\nAdd new semesters? (y/n): ').strip().lower() == 'y':
                    while input('\nAdd semester? (y/n): ').strip().lower() == 'y':
                        y = prompt_positive_int('Year: ', 'Year', 5)
                        s = prompt_positive_int('Sem (1-2): ', 'Sem', 2)
                        g = prompt_positive_float(f'GPA Y{y}S{s}: ', 'GPA', 5.0)
                        if input('CU: (1) per course or (2) total: ').strip() == '1':
                            n = prompt_positive_int('# courses: ', 'Courses')
                            c_cu = sum(prompt_positive_int(f'  Course {i} CU: ', 'CU') for i in range(1, n+1))
                        else:
                            c_cu = prompt_positive_int('Total CU: ', 'CU')
                        wt += g * c_cu
                        cu += c_cu
                        r = round(wt / cu, DECIMAL_PLACES) if cu > 0 else 0.0
                        print_success(f'CGPA: {r}')
                return round(wt / cu, DECIMAL_PLACES) if cu > 0 else 0.0
            elif c == '2':
                break
            print_warning('Enter 1 or 2.')
    print_instruction('Enter GPA and CU for all semesters up to current.')
    yr = prompt_positive_int('Current year (1-5): ', 'Year', 5)
    sm = prompt_positive_int(f'Semester in Y{yr} (1-2): ', 'Sem', 2)
    while sm not in (1, 2):
        sm = prompt_positive_int('Semester (1-2): ', 'Sem', 2)
    total, cu_sum, cnt = 0.0, 0, 0
    tot_s = (yr - 1) * 2 + sm
    if tot_s == 0:
        return 0.0
    print_success(f'Enter GPA and CU for {tot_s} semester(s).')
    for y in range(1, yr + 1):
        for s in range(1, 3):
            cnt += 1
            if y == yr and s == sm:
                pass
            elif y == yr and s > sm:
                break
            print(f'\n--- Year {y}, Sem {s} ---')
            gpa = prompt_positive_float(f'GPA Y{y}S{s}: ', 'GPA', 5.0)
            print('Enter CU: (1) per course or (2) total')
            while True:
                ch = input('Select (1-2): ').strip()
                if ch == '1':
                    n = prompt_positive_int('# courses: ', 'Courses')
                    cu = sum(prompt_positive_int(f'  Course {i} CU: ', 'CU') for i in range(1, n+1))
                    break
                elif ch == '2':
                    cu = prompt_positive_int('Total CU: ', 'CU')
                    break
                print_warning('Enter 1 or 2.')
            total += gpa * cu
            cu_sum += cu
            r = round(total / cu_sum, DECIMAL_PLACES) if cu_sum > 0 else 0.0
            print_info(f'CGPA after {cnt} sem: {r}')
            if y == yr and s == sm:
                break
        if y == yr:
            break
    result = round(total / cu_sum, DECIMAL_PLACES) if cu_sum > 0 else 0.0
    print_success(f'\nFinal CGPA ({tot_s} semesters): {result}')
    return result


def prompt_courses_quick():

    n = int(input("How many courses? ").strip())
    courses = []
    for i in range(n):
        # limit credit unit choices to 1..5 and allow a default of 3
        cu_options = [1,2,3,4,5]
        cu_raw = input(f"Course {i+1} credit units (choose {cu_options}, default 3): ").strip()
        if cu_raw == '':
            cu = 3
        else:
            if not cu_raw.isdigit():
                raise ValueError('Credit units must be a digit')
            cu = int(cu_raw)
            if cu not in cu_options:
                raise ValueError('Credit units must be one of: ' + ','.join(str(x) for x in cu_options))
        grade = prompt_grade(i+1)
        courses.append((cu, grade))
    return courses


def prompt_completed_semesters_total_cu():
    """Prompt user for academic year and semester and collect CUs for completed semesters.

    Returns total_cu (int).
    """
    print('\n-- Historical semesters credit units collector --')
    year = int(input('Current academic year (e.g. 1, 2, 3): ').strip())
    sem = int(input('Current semester (1 or 2): ').strip())
    if year < 1 or sem not in (1,2):
        raise ValueError('Invalid year/semester')

    # compute number of completed semesters (semesters before the current one)
    completed = (year - 1) * 2 + (sem - 1)
    if completed <= 0:
        print('No historical semesters yet.')
        return 0

    total_cu = 0
    cu_options = [1,2,3,4,5]
    print(f'You have {completed} completed semester(s).')
    for s in range(1, completed + 1):
        use_total = input(f'Do you want to enter total credit units for semester {s} directly? (y/n, default y): ').strip().lower() or 'y'
        if use_total == 'y':
            raw = input(f'Enter total credit units for semester {s} (digits only): ').strip()
            if not raw.isdigit():
                raise ValueError('Credit units must be digits')
            sem_total = int(raw)
            if sem_total < 0:
                raise ValueError('Credit units must be non-negative')
            total_cu += sem_total
        else:
            # ask number of courses and CU per course (with fixed options)
            n_courses = int(input(f'Number of courses in semester {s}: ').strip())
            for ci in range(n_courses):
                cu_raw = input(f'  CU for course {ci+1} (choose {cu_options}, default 3): ').strip()
                if cu_raw == '':
                    cu = 3
                else:
                    if not cu_raw.isdigit():
                        raise ValueError('Credit units must be digits')
                    cu = int(cu_raw)
                    if cu not in cu_options:
                        raise ValueError('Credit unit must be one of: ' + ','.join(map(str, cu_options)))
                total_cu += cu

    print(f'Total historical credit units = {total_cu}')
    return total_cu

def cli():
    print_header("GPA & CGPA Simulator (CLI)")
    print_info('Please check your curriculum for accurate Credit Unit (CU) information.')
    print_info('Incorrect CU values will lead to incorrect GPA/CGPA calculations.')
    
    # Authentication menu
    current_user = None
    
    while not current_user:
        print(f"\n{'='*60}")
        print('WELCOME TO GPA SIMULATOR')
        print('='*60)
        print('1. Register new account')
        print('2. Login to existing account')
        print('3. Continue as guest (no saving)')
        print('='*60)
        
        auth_choice = input('\nSelect option (1-3): ').strip()
        
        if auth_choice == '1':
            # Register
            print_header('Register New Account')
            username = input('Enter username: ').strip()
            password = input('Enter password: ').strip()
            full_name = input('Enter full name (optional): ').strip() or None
            email = input('Enter email (optional): ').strip() or None
            program = input('Enter program name (e.g., Computer Science, optional): ').strip() or None
            
            user = vault.register_user(username, password, full_name, email, program)
            if user:
                print_success(f'Account created successfully! Welcome, {full_name or username}!')
                vault.set_current_user(user)
                get_session().set_user(user['id'], user['username'])
                current_user = user
                
                # Offer first-time onboarding
                onboard_first_time_user(user['id'], user['username'])
            else:
                print_warning('Username already exists. Please try another.')
                
        elif auth_choice == '2':
            # Login
            print_header('Login to Your Account')
            username = input('Enter username: ').strip()
            password = input('Enter password: ').strip()
            
            user = vault.login_user(username, password)
            if user:
                print_success(f'Welcome back, {user.get("full_name") or user["username"]}!')
                vault.set_current_user(user)
                get_session().set_user(user['id'], user['username'])
                current_user = user
            else:
                print_warning('Invalid username or password.')
                
        elif auth_choice == '3':
            # Guest mode
            print_info('Continuing as guest. Your data will not be saved.')
            current_user = {'id': None, 'username': 'guest', 'full_name': 'Guest'}
            
        else:
            print_warning('Invalid option. Please select 1, 2, or 3.')
    
    # Main menu
    is_guest = current_user['id'] is None
    
    while True:
        print(f"\n{'='*60}")
        print('MENU OPTIONS:')
        print('  1. Calculate GPA (quick) - for current semester')
        print('  2. Update CGPA - calculate CGPA after current semester')
        print('  3. Calculate CGPA manually - enter all semester grades cumulatively')
        print('  4. Required GPA for target CGPA - what GPA do I need next semester?')
        print('  5. Simulate grade combinations - find possible grades for target GPA')
        if not is_guest:
            print('  6. View academic history')
            print('  7. Save current semester to vault')
            print('  8. Initialize vault database')
            print('  9. Logout')
            print('  10. Exit')
        else:
            print('  6. Initialize vault database')
            print('  7. Exit')
        print(f"{'='*60}")
        
        choice = input('\nSelect option: ').strip()
        try:
            if choice == '1':
                print_header('Calculate Current Semester GPA')
                courses = prompt_courses_quick()
                gpa = compute_gpa(courses)
                if validate_gpa(gpa, "Calculated GPA"):
                    print_success(f'Your current semester GPA = {gpa}')
                else:
                    print_instruction('Please review your grades and credit units, then try again.')
                    
            elif choice == '2':
                print_header('Update CGPA')
                
                if is_guest:
                    # Guest mode - use old manual flow
                    print_instruction('STEP 1: Enter your OLD CGPA (before current semester)')
                    print_info('This is the CGPA you had before you completed your current semester.')
                    old_cgpa = prompt_positive_float('Enter old CGPA (0.0 - 5.0): ', 'Old CGPA', MAX_GPA)
                    
                    print_instruction('STEP 2: Enter total credit units completed BEFORE current semester')
                    old_cu = calculate_total_cu_helper()
                    
                    print_instruction('STEP 3: Enter your CURRENT SEMESTER GPA')
                    print_info('This is the GPA you calculated for your most recent semester.')
                    new_gpa = prompt_positive_float('Enter current semester GPA (0.0 - 5.0): ', 'Current GPA', MAX_GPA)
                    
                    print_instruction('STEP 4: Enter credit units for CURRENT SEMESTER')
                    new_cu = prompt_positive_int('Enter current semester credit units: ', 'Current semester CU')
                else:
                    # Logged-in mode - smart defaults with vault data
                    old_cgpa, old_cu, new_gpa, new_cu = prompt_update_cgpa_with_defaults(current_user['id'])
                
                new_cgpa = update_cgpa(old_cgpa, old_cu, new_gpa, new_cu)
                if validate_gpa(new_cgpa, "Calculated CGPA"):
                    print_success(f'Your new CGPA = {new_cgpa}')
                    
                    # Offer to save this semester
                    if not is_guest:
                        confirm = input('\nWould you like to save this calculation? (y/n): ').strip().lower()
                        if confirm == 'y':
                            year = prompt_positive_int('Academic year (1-5): ', 'Academic year', max_val=5)
                            sem = prompt_positive_int('Semester number (1 or 2): ', 'Semester number', max_val=2)
                            courses_tuples = []  # No courses recorded in this quick flow
                            vault.save_semester(current_user['id'], year, sem, new_cu, new_gpa, new_cgpa, courses_tuples)
                            print_success('Semester saved to vault!')
                else:
                    print_instruction('Your inputs resulted in an invalid CGPA. Please verify:')
                    print('  - Old CGPA is not more than 5.0')
                    print('  - Current semester GPA is not more than 5.0')
                    print('  - Credit units are reasonable')
                    
            elif choice == '3':
                print_header('Calculate CGPA Manually - All Semesters')
                if is_guest:
                    cgpa = calculate_cgpa_from_scratch()
                else:
                    cgpa = calculate_cgpa_from_scratch_with_vault(current_user['id'])
                if validate_gpa(cgpa, "Calculated CGPA"):
                    print_success(f'Your cumulative CGPA = {cgpa}')
                else:
                    print_instruction('Your inputs resulted in an invalid CGPA. Please verify:')
                    print('  - All semester GPAs are not more than 5.0')
                    print('  - Credit units are reasonable and match your curriculum')
                    
            elif choice == '4':
                print_header('Required GPA for Target CGPA')
                
                print_instruction('STEP 1: Enter your OLD CGPA (before upcoming semester)')
                old_cgpa = prompt_positive_float('Enter old CGPA (0.0 - 5.0): ', 'Old CGPA', MAX_GPA)
                
                print_instruction('STEP 2: Enter total credit units completed BEFORE upcoming semester')
                old_cu = calculate_total_cu_helper()
                
                print_instruction('STEP 3: Enter credit units for UPCOMING SEMESTER')
                new_cu = prompt_positive_int('Enter upcoming semester credit units: ', 'Upcoming semester CU')
                
                print_instruction('STEP 4: Enter your TARGET CGPA (what you want to achieve)')
                target = prompt_positive_float('Enter target CGPA (0.0 - 5.0): ', 'Target CGPA', MAX_GPA)
                
                required = required_gpa_for_target(old_cgpa, old_cu, new_cu, target)
                # Round for display
                required_display = round(required, DECIMAL_PLACES)

                # If required GPA is above the maximum achievable in one semester, give friendly guidance
                if required > MAX_GPA:
                    print_warning(f'You would need a GPA of {required_display} in the upcoming semester to reach a CGPA of {target}.')
                    print_instruction(f'However, the maximum possible GPA is {MAX_GPA}, so this is not achievable in a single semester.')
                    print_info('Options:')
                    print('  - Lower your target CGPA to a more realistic value.')
                    print('  - Spread the improvement across multiple future semesters (improve gradually).')
                    print('  - Review your entered credit units and previous CGPA for accuracy.')
                else:
                    print_success(f'You need a GPA of {required_display} in the upcoming semester to reach your target CGPA of {target}')
                    
            elif choice == '5':
                print_header('Simulate Grade Combinations for Target GPA')
                
                print_instruction('Enter details for the current semester you want to simulate.')
                n = prompt_positive_int('How many courses in this semester? ', 'Number of courses')
                
                cus = []
                print_instruction('Please check your curriculum for credit units per course.')
                for i in range(n):
                    cu = prompt_positive_int(f'Course {i+1} credit units (default is usually 3): ', f'Course {i+1} CU')
                    cus.append(cu)
                
                target = prompt_positive_float('Enter your target semester GPA (0.0 - 5.0): ', 'Target GPA', MAX_GPA)
                
                # Calculate achievable range
                min_possible = min(GRADE_POINTS.values())
                max_possible = max(GRADE_POINTS.values())
                total_cu = sum(cus)
                min_gpa_achievable = sum(c * min_possible for c in cus) / total_cu
                max_gpa_achievable = sum(c * max_possible for c in cus) / total_cu
                min_gpa_achievable = round(min_gpa_achievable, DECIMAL_PLACES)
                max_gpa_achievable = round(max_gpa_achievable, DECIMAL_PLACES)
                
                # Validate target is achievable
                if target < min_gpa_achievable or target > max_gpa_achievable:
                    print_warning(f'Target GPA {target} is outside the achievable range.')
                    print_instruction(f'Your achievable range with these courses is {min_gpa_achievable} to {max_gpa_achievable}.')
                    print('Please set a target within this range and try again.')
                else:
                    results = generate_grade_combinations(n, cus, target)
                    if not results:
                        print_warning('Unable to find grade combinations at this moment.')
                        print_instruction('This rarely happens. Please try:')
                        print('  - Adjusting your target GPA slightly (e.g., 3.99 instead of 4.0)')
                        print('  - Verifying your credit unit values are correct')
                    else:
                        print_success(f'Found {len(results)} realistic grade combination(s) for target GPA {target}:')
                        print_info('[NOTE] These are simulations with slight variations. Actual results may vary slightly.')
                        
                        # Pagination: show 5 results at a time
                        results_per_page = 5
                        total_pages = (len(results) + results_per_page - 1) // results_per_page
                        current_page = 0
                        
                        while current_page < total_pages:
                            start_idx = current_page * results_per_page
                            end_idx = min(start_idx + results_per_page, len(results))
                            
                            print('\n' + '='*60)
                            for i, (grades, gpa) in enumerate(results[start_idx:end_idx], start_idx + 1):
                                print(f'\n{i}. Grades: {grades}')
                                print(f'   GPA: {gpa}')
                            
                            # Show pagination info
                            if total_pages > 1:
                                print('\n' + '='*60)
                                print(f'Page {current_page + 1} of {total_pages}')
                                
                                if current_page < total_pages - 1:
                                    next_choice = input('View more results? (y/n): ').strip().lower()
                                    if next_choice == 'y':
                                        current_page += 1
                                        continue
                                    else:
                                        break
                            
                            # Display course flexibility note (only on last page or if no pagination)
                            if current_page == total_pages - 1 or total_pages == 1:
                                from collections import Counter
                                cu_counts = Counter(cus)
                                same_cu_groups = [cu for cu, count in cu_counts.items() if count >= 2]
                                
                                if same_cu_groups:
                                    print('\n' + '='*60)
                                    print_info('[TIP] GRADE FLEXIBILITY NOTE:')
                                    print('You can exchange grades between courses with the same credit units.')
                                    for cu_val in sorted(same_cu_groups):
                                        course_indices = [idx + 1 for idx, cu in enumerate(cus) if cu == cu_val]
                                        print(f'  Courses {course_indices} all have {cu_val} CU - grades can be swapped')
                                    print('This gives you more flexibility in planning your study effort.')
                                print('='*60)
                            
                            break
                        
            elif choice == '6':
                if is_guest:
                    print_header('Initialize Vault Database')
                    vault.init_db()
                    print_success('Vault DB initialized at app/database/vault.db')
                else:
                    print_header('View Academic History')
                    semesters = vault.get_semesters_for_user(current_user['id'])
                    if not semesters:
                        print_info('No academic records found. Start by saving a semester.')
                    else:
                        print_success(f'Found {len(semesters)} semester(s):')
                        print()
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
                                    print(f"    - {course['name']}: {course['grade_letter']} ({course['credit_units']} CU)")
                            print()
                        
            elif choice == '7':
                if is_guest:
                    print_success('Goodbye! Good luck with your studies!')
                    break
                else:
                    print_header('Save Current Semester to Vault')
                    
                    print_instruction('STEP 1: Enter academic year and semester number')
                    academic_year = prompt_positive_int('Academic year (1-5): ', 'Academic year', max_val=5)
                    semester_num = prompt_positive_int('Semester number (1 or 2): ', 'Semester number', max_val=2)
                    
                    print_instruction('STEP 2: Enter courses for this semester')
                    n = prompt_positive_int('How many courses in this semester? ', 'Number of courses')
                    
                    courses = []
                    total_cu = 0
                    total_gp = 0
                    
                    for i in range(n):
                        course_name = input(f'Course {i+1} name (e.g., Math 101): ').strip()
                        if not course_name:
                            course_name = f'Course {i+1}'
                        
                        cu = prompt_positive_int(f'Course {i+1} credit units: ', f'Course {i+1} CU')
                        grade = prompt_grade(i+1)
                        
                        courses.append({
                            'name': course_name,
                            'credit_units': cu,
                            'grade_letter': grade
                        })
                        
                        total_cu += cu
                        total_gp += GRADE_POINTS[grade] * cu
                    
                    gpa = round(total_gp / total_cu, DECIMAL_PLACES) if total_cu > 0 else 0.0
                    
                    # Calculate CGPA after adding this semester
                    cgpa = vault.calculate_current_cgpa_with_new_semester(current_user['id'], gpa, total_cu)
                    cgpa = round(cgpa, DECIMAL_PLACES)
                    
                    print_success(f'Semester GPA: {gpa}')
                    print_success(f'CGPA after this semester: {cgpa}')
                    
                    confirm = input('Save this semester to vault? (y/n): ').strip().lower()
                    if confirm == 'y':
                        # Convert courses dict to tuples for vault storage
                        courses_tuples = [(c['name'], c['credit_units'], c['grade_letter']) for c in courses]
                        vault.save_semester(current_user['id'], academic_year, semester_num, total_cu, gpa, cgpa, courses_tuples)
                        print_success('Semester saved successfully!')
                    else:
                        print_info('Semester not saved.')
                        
            elif choice == '8':
                if not is_guest:
                    print_header('Initialize Vault Database')
                    vault.init_db()
                    print_success('Vault DB initialized at app/database/vault.db')
                else:
                    print_warning('Invalid choice. Please select option 1-7.')
                    
            elif choice == '9':
                if not is_guest:
                    print_header('Logging out...')
                    vault.logout_user()
                    reset_session()
                    print_success('Logged out successfully!')
                    break
                else:
                    print_warning('Invalid choice. Please select option 1-7.')
                    
            elif choice == '10':
                if not is_guest:
                    print_success('Goodbye! Good luck with your studies!')
                    break
                else:
                    print_warning('Invalid choice. Please select option 1-7.')
            else:
                if is_guest:
                    print_warning('Invalid choice. Please select option 1-7.')
                else:
                    print_warning('Invalid choice. Please select option 1-10.')
                
        except Exception as e:
            print_warning(f'An error occurred: {e}')
            print_instruction('Please review your inputs and try again.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', action='store_true', help='Run interactive CLI')
    parser.add_argument('--init-db', action='store_true', help='Initialize local sqlite DB')
    args = parser.parse_args()
    if args.init_db:
        vault.init_db()
        print('DB initialized at app/database/vault.db')
    elif args.cli:
        cli()
    else:
        print('No flag passed. Use --cli for interactive terminal or run uvicorn to start API.')
