from .utils import truncate
from .constants import DECIMAL_PLACES

def update_cgpa(old_cgpa: float, old_total_cu: int, new_gpa: float, new_cu: int) -> float:
    if old_total_cu < 0 or new_cu <= 0:
        raise ValueError("Credit units must be positive (old_total_cu >=0, new_cu >0)")
    combined = ((old_cgpa * old_total_cu) + (new_gpa * new_cu)) / (old_total_cu + new_cu)
    return truncate(combined, DECIMAL_PLACES)

def required_gpa_for_target(old_cgpa: float, old_total_cu: int, new_cu: int, target_cgpa: float) -> float:
    numerator = target_cgpa * (old_total_cu + new_cu) - (old_cgpa * old_total_cu)
    required = numerator / new_cu
    return truncate(required, DECIMAL_PLACES)
