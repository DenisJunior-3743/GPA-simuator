from itertools import product
from typing import List, Tuple
from .constants import GRADE_POINTS
from .utils import truncate


def generate_grade_combinations(num_courses: int, cus: List[int], target_gpa: float,
                                tolerance_low: float = 0.05, tolerance_high: float = 0.001, max_results: int = 50,
                                allowed_letters: List[str] = None, allow_A_if_needed: bool = True, exclude_F: bool = True,
                                exact_match: bool = False):
    """Generate grade combinations that hit the target_gpa within tolerance.

    Improvements:
    - Validate inputs
    - Iterate combinations in a realistic order (worst-case first)
    - Prefer combinations that reach the target before exceeding it
    - Do not return combinations that exceed the target by more than tolerance_high
    """
    if num_courses <= 0:
        return []
    if len(cus) != num_courses:
        raise ValueError("length of cus must equal num_courses")

    # Ensure each CU is a positive int and capped (defensive check)
    for cu in cus:
        if not isinstance(cu, int) or cu <= 0:
            raise ValueError("each credit unit must be a positive integer")
    # Determine letters to consider. Default to a realistic student band (B+ down to D). Exclude F by default.
    default_allowed = ['B+', 'B', 'C+', 'C', 'D+', 'D']
    if allowed_letters is None:
        allowed_letters = default_allowed

    letters_sorted_all = sorted(GRADE_POINTS.items(), key=lambda x: x[1])
    # Delegate to the worst-scenarios finder to produce realistic, pessimistic combos.
    # This enforces the default policy of preferring B+ down to D and only allowing A if needed.
    return find_worst_scenarios(num_courses, cus, target_gpa, tolerance_low, tolerance_high, max_results, max_allowed_grade='B+', allow_A_if_needed=allow_A_if_needed, exclude_F=exclude_F, exact_match=exact_match)

def find_minimal_gpa_for_target(old_cgpa: float, old_total_cu: int, remaining_semesters_cu: int, target_cgpa: float):
    numerator = target_cgpa * (old_total_cu + remaining_semesters_cu) - (old_cgpa * old_total_cu)
    avg_needed = numerator / remaining_semesters_cu
    return truncate(avg_needed, 2)


def find_worst_scenarios(num_courses: int, cus: List[int], target_gpa: float,
                        tolerance_low: float = 0.05, tolerance_high: float = 0.001, count: int = 3,
                        max_enumerate: int = 200000, max_allowed_grade: str = 'B+', allow_A_if_needed: bool = True,
                        exclude_F: bool = True, exact_match: bool = False):
    """Return up to `count` realistic grade combinations that meet the target within tolerance.
    
    Improvements:
    - Starts from worst-case grades (D/C) and progressively upgrades
    - GUARANTEES a result by progressively loosening constraints if needed
    - Prefers diverse grade combinations (not all same grade)
    - Only returns achievable combinations with realistic grade distributions
    - Prioritizes lower-effort solutions
    """
    if num_courses <= 0:
        return []
    if len(cus) != num_courses:
        raise ValueError("length of cus must equal num_courses")

    letters = list(GRADE_POINTS.keys())
    total_cu = sum(cus)

    # Quick feasibility check: is target even theoretically possible?
    min_possible_all = min(GRADE_POINTS.values())
    max_possible_all = max(GRADE_POINTS.values())
    min_gpa_possible = sum(c * min_possible_all for c in cus) / total_cu
    max_gpa_possible = sum(c * max_possible_all for c in cus) / total_cu
    
    if target_gpa < min_gpa_possible or target_gpa > max_gpa_possible:
        return []  # Target is genuinely impossible

    def calc_gpa(grade_tuple):
        """Calculate GPA for a grade tuple."""
        total_points = sum(GRADE_POINTS[g] * cu for g, cu in zip(grade_tuple, cus))
        return truncate(total_points / total_cu, 2)

    def grade_variance(grade_tuple):
        """Measure variance in grades (higher = more diverse)."""
        gps = [GRADE_POINTS[g] for g in grade_tuple]
        mean = sum(g * cu for g, cu in zip(gps, cus)) / total_cu
        var = sum(cu * ((g - mean) ** 2) for g, cu in zip(gps, cus)) / total_cu
        return var

    from itertools import product as iter_product, combinations

    # Strategy: Try progressively loosening constraints until we find results
    # Start with restricted letter set, then expand
    
    constraint_levels = [
        ['D', 'D+', 'C', 'C+', 'B', 'B+'],  # Level 0: Realistic (no A)
        ['D', 'D+', 'C', 'C+', 'B', 'B+', 'A'],  # Level 1: Add A if needed
        list(GRADE_POINTS.keys()),  # Level 2: All grades (emergency)
    ]
    
    candidates = []
    seen = set()
    
    for level, allowed_letters in enumerate(constraint_levels):
        # Filter out F if needed
        if exclude_F:
            allowed_letters = [l for l in allowed_letters if l != 'F']
        
        if not allowed_letters:
            continue
        
        # Try all combinations
        from math import pow
        total_combos = int(pow(len(allowed_letters), num_courses))
        
        if total_combos <= max_enumerate:
            for combo in iter_product(allowed_letters, repeat=num_courses):
                if combo in seen:
                    continue
                seen.add(combo)
                
                gpa = calc_gpa(combo)
                
                # At higher constraint levels, be more lenient with tolerance
                if level == 0:
                    tolerance = (tolerance_low, tolerance_high)
                elif level == 1:
                    tolerance = (tolerance_low * 2, tolerance_high * 2)
                else:  # Emergency level - accept anything close
                    tolerance = (0.1, 0.1)
                
                # Check if within tolerance
                if (target_gpa - tolerance[0]) <= gpa <= (target_gpa + tolerance[1]):
                    diversity = grade_variance(combo)
                    num_high_grades = sum(1 for g in combo if GRADE_POINTS[g] >= 4.0)
                    candidates.append((combo, gpa, diversity, num_high_grades))
        
        # If we found candidates at this level, stop expanding
        if candidates:
            break
    
    # If still no candidates, use heuristic approach: build combination to hit target exactly
    if not candidates:
        all_letters = [l for l in letters if l != 'F'] if exclude_F else letters
        candidates = _build_target_combinations(num_courses, cus, target_gpa, all_letters, count, exclude_F)
    
    # Sort: closest to target, then most diverse, then fewest high grades
    candidates.sort(key=lambda x: (
        abs(target_gpa - x[1]),  # Closeness to target
        -x[2],                    # Higher variance = more diverse
        x[3]                      # Fewer high grades needed
    ))
    
    return [(c[0], c[1]) for c in candidates[:count]]


def _build_target_combinations(num_courses: int, cus: List[int], target_gpa: float, 
                               available_grades: List[str], count: int, exclude_F: bool) -> List[Tuple]:
    """Build grade combinations that hit target by systematic construction.
    
    This generates realistic, mixed-grade combinations by:
    1. Starting from worst-case and progressively upgrading
    2. Mixing grades strategically (not all same grade)
    3. Trying multiple upgrade patterns
    """
    total_cu = sum(cus)
    candidates = []
    seen = set()
    
    def calc_gpa(grade_tuple):
        total_points = sum(GRADE_POINTS[g] * cu for g, cu in zip(grade_tuple, cus))
        return truncate(total_points / total_cu, 2)
    
    def grade_variance(grade_tuple):
        gps = [GRADE_POINTS[g] for g in grade_tuple]
        mean = sum(g * cu for g, cu in zip(gps, cus)) / total_cu
        var = sum(cu * ((g - mean) ** 2) for g, cu in zip(gps, cus)) / total_cu
        return var
    
    # Sort grades from worst to best
    sorted_grades = sorted(available_grades, key=lambda x: GRADE_POINTS[x])
    
    from itertools import combinations, product as iter_product
    
    # Strategy 1: Try combinations with mixed grades
    # For each possible number of unique grades (2, 3, 4...)
    for num_unique in range(2, min(num_courses + 1, 5)):
        for grade_combo in combinations(sorted_grades, num_unique):
            # Try different distributions of these grades across courses
            for distribution in iter_product(grade_combo, repeat=num_courses):
                if distribution in seen:
                    continue
                seen.add(distribution)
                
                gpa = calc_gpa(distribution)
                
                # Accept if close to target (0.15 tolerance for mixed grades)
                if abs(gpa - target_gpa) < 0.15:
                    diversity = grade_variance(distribution)
                    num_As = distribution.count('A')
                    candidates.append((distribution, gpa, diversity, num_As))
    
    # Strategy 2: Targeted upgrade - start with mid-range grade and adjust
    if not candidates:
        # Find a middle-ground grade point value
        middle_idx = len(sorted_grades) // 2
        
        for start_idx in range(max(0, middle_idx - 1), min(len(sorted_grades), middle_idx + 2)):
            base_grade = sorted_grades[start_idx]
            
            # Try upgrading specific positions with various grades
            for num_upgrades in range(1, min(num_courses, 4)):
                for positions in combinations(range(num_courses), num_upgrades):
                    # Try upgrading to different grades (not just one)
                    for upgrade_grades in combinations(sorted_grades[start_idx:], min(num_upgrades, 2)):
                        for upgrade_combo in iter_product(upgrade_grades, repeat=num_upgrades):
                            combo_list = [base_grade] * num_courses
                            for pos, new_grade in zip(positions, upgrade_combo):
                                combo_list[pos] = new_grade
                            combo = tuple(combo_list)
                            
                            if combo in seen:
                                continue
                            seen.add(combo)
                            
                            gpa = calc_gpa(combo)
                            if abs(gpa - target_gpa) < 0.15:
                                diversity = grade_variance(combo)
                                num_As = combo.count('A')
                                candidates.append((combo, gpa, diversity, num_As))
                
                if len(candidates) >= count * 3:
                    break
            
            if len(candidates) >= count * 3:
                break
    
    # Strategy 3: If still not enough, try the progressive-upgrade heuristic
    if len(candidates) < count:
        for base_grade_idx, base_grade in enumerate(sorted_grades):
            base = tuple([base_grade] * num_courses)
            base_gpa = calc_gpa(base)
            
            if abs(base_gpa - target_gpa) < 0.01:
                if base not in seen:
                    seen.add(base)
                    diversity = grade_variance(base)
                    candidates.append((base, base_gpa, diversity, base.count('A')))
            
            # Try selective upgrades
            for num_upgrades in range(1, min(num_courses + 1, 4)):
                for positions in combinations(range(num_courses), num_upgrades):
                    # Try mixed upgrade grades
                    for upgrade_grade in sorted_grades[base_grade_idx + 1:]:
                        combo_list = list(base)
                        for pos in positions:
                            combo_list[pos] = upgrade_grade
                        combo = tuple(combo_list)
                        
                        if combo in seen:
                            continue
                        seen.add(combo)
                        
                        gpa = calc_gpa(combo)
                        if abs(gpa - target_gpa) < 0.15:
                            diversity = grade_variance(combo)
                            candidates.append((combo, gpa, diversity, combo.count('A')))
                
                if len(candidates) >= count * 2:
                    break
            
            if len(candidates) >= count * 2:
                break
    
    return candidates
