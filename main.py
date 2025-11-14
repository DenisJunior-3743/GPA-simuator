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
    print(f"\n📋 INSTRUCTION: {text}")

def print_warning(text: str):
    """Print a warning message."""
    print(f"\n⚠️  WARNING: {text}")

def print_info(text: str):
    """Print info message."""
    print(f"\nℹ️  INFO: {text}")

def print_success(text: str):
    """Print success message."""
    print(f"\n✅ {text}")

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
    
    while True:
        print(f"\n{'='*60}")
        print('MENU OPTIONS:')
        print('  1. Calculate GPA (quick) - for current semester')
        print('  2. Update CGPA - calculate CGPA after current semester')
        print('  3. Calculate CGPA manually - enter all semester grades cumulatively')
        print('  4. Required GPA for target CGPA - what GPA do I need next semester?')
        print('  5. Simulate grade combinations - find possible grades for target GPA')
        print('  6. Initialize vault database')
        print('  7. Exit')
        print(f"{'='*60}")
        
        choice = input('\nSelect option (1-7): ').strip()
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
                
                new_cgpa = update_cgpa(old_cgpa, old_cu, new_gpa, new_cu)
                if validate_gpa(new_cgpa, "Calculated CGPA"):
                    print_success(f'Your new CGPA = {new_cgpa}')
                else:
                    print_instruction('Your inputs resulted in an invalid CGPA. Please verify:')
                    print('  - Old CGPA is not more than 5.0')
                    print('  - Current semester GPA is not more than 5.0')
                    print('  - Credit units are reasonable')
                    
            elif choice == '3':
                print_header('Calculate CGPA Manually - All Semesters')
                cgpa = calculate_cgpa_from_scratch()
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
                        print('\n' + '='*60)
                        for i, (grades, gpa) in enumerate(results, 1):
                            print(f'\n{i}. Grades: {grades}')
                            print(f'   GPA: {gpa}')
                        
                        # Display course flexibility note
                        from collections import Counter
                        cu_counts = Counter(cus)
                        same_cu_groups = [cu for cu, count in cu_counts.items() if count >= 2]
                        
                        if same_cu_groups:
                            print('\n' + '='*60)
                            print_info('💡 GRADE FLEXIBILITY NOTE:')
                            print('You can exchange grades between courses with the same credit units.')
                            for cu_val in sorted(same_cu_groups):
                                course_indices = [idx + 1 for idx, cu in enumerate(cus) if cu == cu_val]
                                print(f'  Courses {course_indices} all have {cu_val} CU - grades can be swapped')
                            print('This gives you more flexibility in planning your study effort.')
                        print('='*60)
                        
            elif choice == '6':
                print_header('Initialize Vault Database')
                vault.init_db()
                print_success('Vault DB initialized at app/database/vault.db')
                
            elif choice == '7':
                print_success('Goodbye! Good luck with your studies!')
                break
            else:
                print_warning('Invalid choice. Please select option 1-7.')
                
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
