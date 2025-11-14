from app.constants import GRADE_POINTS
from itertools import product

allowed = ['B+','B','C+','C','D+','D','F']
all_letters = [l for l,_ in sorted(GRADE_POINTS.items(), key=lambda x:x[1])]
letters = [l for l in all_letters if l in allowed]
print('letters:', letters)

gp = [GRADE_POINTS[l] for l in letters]
print('gp:', gp)

cus = [3,3,3,3,3]
total = sum(cus)
found = []
for combo in product(range(len(letters)), repeat=5):
    total_points = sum(cus[i]*gp[combo[i]] for i in range(5))
    gpa = total_points/total
    if (4.0 - 0.05) <= gpa <= (4.0 + 0.4):
        found.append((tuple(letters[i] for i in combo), round(gpa,2)))
        if len(found) >= 10:
            break

print('found:', found)
