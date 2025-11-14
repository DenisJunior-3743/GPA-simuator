from decimal import Decimal, ROUND_DOWN
from typing import List, Tuple

def truncate(value: float, places: int) -> float:
    if places < 0:
        raise ValueError("places must be >= 0")
    q = Decimal(10) ** -places
    d = Decimal(value).quantize(q, rounding=ROUND_DOWN)
    return float(d)

def validate_grade_letter(letter: str, grade_map: dict) -> str:
    if not isinstance(letter, str):
        raise ValueError("grade must be a string")
    l = letter.strip().upper()
    if l not in grade_map:
        raise ValueError(f"Unknown grade letter: {letter}")
    return l

def weighted_average(pairs: List[Tuple[float, float]]) -> float:
    total_weight = sum(w for w, _ in pairs)
    if total_weight == 0:
        return 0.0
    return sum(w * v for w, v in pairs) / total_weight
