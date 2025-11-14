from typing import List, Tuple
from .constants import GRADE_POINTS, DECIMAL_PLACES
from .utils import validate_grade_letter

def compute_gpa(courses: List[Tuple[int, str]]) -> float:
    if len(courses) == 0:
        return 0.0
    total_points = 0.0
    total_cu = 0
    for cu, letter in courses:
        if cu <= 0:
            raise ValueError("Credit units must be positive integers.")
        letter = validate_grade_letter(letter, GRADE_POINTS)
        gp = GRADE_POINTS[letter]
        total_points += cu * gp
        total_cu += cu
    raw = total_points / total_cu if total_cu > 0 else 0.0
    return round(raw, DECIMAL_PLACES)
