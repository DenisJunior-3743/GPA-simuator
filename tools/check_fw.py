from app.constants import GRADE_POINTS
from itertools import product

letters = list(GRADE_POINTS.keys())
print('letters all:', letters)
allowed_letters = [l for l in letters if GRADE_POINTS[l] <= GRADE_POINTS['B+']]
print('allowed letters:', allowed_letters)
idx_map_allowed = [letters.index(l) for l in allowed_letters]
print('idx_map_allowed:', idx_map_allowed)

cus = [3,3,3,3,3]
total_cu = sum(cus)
found = []
for combo in product(idx_map_allowed, repeat=5):
    total_points = 0.0
    for idx, gidx in enumerate(combo):
        total_points += cus[idx] * list(GRADE_POINTS.values())[gidx]
    gpa = total_points / total_cu
    if (4.0 - 0.0) <= gpa <= (4.0 + 0.4):
        found.append((tuple(list(GRADE_POINTS.keys())[i] for i in combo), round(gpa,2)))
        if len(found) >= 10:
            break

print('found:', found)
