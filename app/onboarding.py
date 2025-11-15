"""Onboarding flow for first-time users.

Guides new users through setting up their academic history without redundant data entry.
"""

from typing import List, Tuple, Dict
from . import vault_manager as vault
from .constants import GRADE_POINTS


def print_section(text: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_instruction(text: str):
    """Print instruction text."""
    print(f"\n[INSTRUCTION] {text}")


def print_info(text: str):
    """Print info text."""
    print(f"\n[INFO] {text}")


def print_success(text: str):
    """Print success text."""
    print(f"\n[SUCCESS] {text}")


def print_warning(text: str):
    """Print warning text."""
    print(f"\n[WARNING] {text}")


def prompt_positive_int(prompt_text: str, label: str = "Value", max_val: int = None) -> int:
    """Prompt for positive integer with validation."""
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


def prompt_positive_float(prompt_text: str, label: str = "Value", max_val: float = None) -> float:
    """Prompt for positive float with validation."""
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


def display_grade_menu():
    """Display available grades."""
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


def collect_semester_data_quick(year: int, sem: int) -> Tuple[int, float]:
    """Collect CU and GPA for a semester (quick mode - no courses recorded).
    
    Returns: (total_cu, gpa)
    """
    print(f"\n--- Year {year}, Semester {sem} ---")
    
    # Ask how user wants to enter CU
    print_instruction('How would you like to enter CU for this semester?')
    print('  1. Enter total CU for semester directly')
    print('  2. Enter CU per course (we will sum them)')
    
    while True:
        cu_choice = input('Select option (1 or 2): ').strip()
        if cu_choice == '1':
            total_cu = prompt_positive_int(f'Enter total CU for Year {year}, Semester {sem}: ', 'Semester CU')
            break
        elif cu_choice == '2':
            n_courses = prompt_positive_int(f'How many courses in Year {year}, Semester {sem}? ', 'Number of courses')
            total_cu = 0
            for course_num in range(1, n_courses + 1):
                cu_val = prompt_positive_int(f'  Course {course_num} CU: ', 'CU')
                total_cu += cu_val
            break
        else:
            print_warning('Please enter 1 or 2.')
    
    print_success(f'Total CU for Year {year}, Semester {sem}: {total_cu}')
    
    # Ask for GPA
    gpa = prompt_positive_float(f'Enter GPA for Year {year}, Semester {sem} (0.0 - 5.0): ', 'Semester GPA', max_val=5.0)
    
    return (total_cu, gpa)


def collect_semester_data_detailed(year: int, sem: int) -> Tuple[int, float, List[Tuple[str, int, str]]]:
    """Collect full semester data including course details.
    
    Returns: (total_cu, gpa, courses_list)
    """
    print(f"\n--- Year {year}, Semester {sem} ---")
    
    n_courses = prompt_positive_int(f'How many courses in Year {year}, Semester {sem}? ', 'Number of courses')
    
    courses = []
    total_cu = 0
    total_gp = 0
    
    for i in range(n_courses):
        course_name = input(f'Course {i+1} name (optional, press Enter to skip): ').strip()
        if not course_name:
            course_name = f'Course {i+1}'
        
        cu = prompt_positive_int(f'Course {i+1} credit units: ', f'Course {i+1} CU')
        grade = prompt_grade(i+1)
        
        courses.append((course_name, cu, grade))
        total_cu += cu
        total_gp += GRADE_POINTS[grade] * cu
    
    gpa = round(total_gp / total_cu, 2) if total_cu > 0 else 0.0
    
    return (total_cu, gpa, courses)


def onboard_first_time_user(user_id: int, username: str) -> bool:
    """Onboard a first-time user by collecting their academic history.
    
    Returns: True if successful, False if user skips onboarding.
    """
    print_section('Academic History Setup')
    print_instruction('Welcome! Let\'s set up your academic history so you don\'t have to re-enter data later.')
    
    # Ask if user wants to set up history now
    setup_now = input('Set up your academic history now? (y/n, you can skip for later): ').strip().lower()
    if setup_now != 'y':
        print_info('You can set up your history anytime by saving semesters manually.')
        return False
    
    # Collect basic info
    current_year = prompt_positive_int('What year are you currently in? (1-5): ', 'Current year', max_val=5)
    current_sem = prompt_positive_int(f'What semester in year {current_year}? (1 or 2): ', 'Current semester', max_val=2)
    
    # Validate and calculate total semesters
    total_semesters = (current_year - 1) * 2 + current_sem
    
    print_info(f'You have {total_semesters} semester(s) to account for.')
    
    # Ask about detail level
    print_instruction('Do you want to:')
    print('  1. Quick entry - just total CU and GPA per semester (faster)')
    print('  2. Detailed entry - include course names and grades (more complete)')
    
    detail_choice = input('Select option (1 or 2): ').strip()
    use_detailed = detail_choice == '2'
    
    # Collect data for each semester
    print_section('Entering Semester Data')
    print_info(f'Enter data for {total_semesters} semester(s). Press Enter for defaults where shown.')
    
    all_semesters = []
    total_cgpa_gp = 0
    total_cgpa_cu = 0
    
    for year_num in range(1, current_year + 1):
        for sem_num in range(1, 3):
            # Stop after current semester
            if year_num == current_year and sem_num > current_sem:
                break
            
            if use_detailed:
                total_cu, gpa, courses = collect_semester_data_detailed(year_num, sem_num)
                courses_tuples = courses
            else:
                total_cu, gpa = collect_semester_data_quick(year_num, sem_num)
                courses_tuples = []
            
            # Calculate running CGPA
            total_cgpa_gp += gpa * total_cu
            total_cgpa_cu += total_cu
            running_cgpa = round(total_cgpa_gp / total_cgpa_cu, 2) if total_cgpa_cu > 0 else 0.0
            
            all_semesters.append({
                'year': year_num,
                'sem': sem_num,
                'total_cu': total_cu,
                'gpa': gpa,
                'cgpa': running_cgpa,
                'courses': courses_tuples
            })
            
            print_success(f'Year {year_num}, Sem {sem_num}: GPA={gpa}, CU={total_cu}, CGPA={running_cgpa}')
    
    # Review and confirm
    print_section('Review Your Data')
    print_info('Summary of your academic history:')
    print(f'\n{"Year":<6} {"Sem":<5} {"GPA":<8} {"CU":<8} {"CGPA":<8}')
    print('-' * 35)
    for sem in all_semesters:
        print(f'{sem["year"]:<6} {sem["sem"]:<5} {sem["gpa"]:<8.2f} {sem["total_cu"]:<8} {sem["cgpa"]:<8.2f}')
    
    # Ask for confirmation
    confirm = input('\nSave this data to your vault? (y/n): ').strip().lower()
    if confirm != 'y':
        print_warning('Data not saved. You can add semesters later using the save option.')
        return False
    
    # Save to vault
    try:
        for sem in all_semesters:
            vault.save_semester(
                user_id=user_id,
                academic_year=sem['year'],
                semester_num=sem['sem'],
                total_cu=sem['total_cu'],
                gpa=sem['gpa'],
                cgpa=sem['cgpa'],
                courses=sem['courses'] if sem['courses'] else None
            )
        
        print_success(f'✅ Academic history saved! {len(all_semesters)} semester(s) added to your vault.')
        print_info(f'Your current CGPA: {all_semesters[-1]["cgpa"]}')
        return True
        
    except Exception as e:
        print_warning(f'Error saving to vault: {e}')
        return False
