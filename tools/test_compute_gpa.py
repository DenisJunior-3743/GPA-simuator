import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.gpa_calculator import compute_gpa

# Basic tests
assert compute_gpa([]) == 0.0
assert compute_gpa([(3,'A')]) == 5.0
assert compute_gpa([(3,'A'),(3,'B')]) == round((3*5.0 + 3*4.0)/6,2)

# Test invalid CU
try:
    compute_gpa([(0,'A')])
    raise SystemExit('Expected ValueError for zero CU')
except ValueError:
    pass

# Test invalid grade
try:
    compute_gpa([(3,'Z')])
    raise SystemExit('Expected ValueError for unknown grade')
except ValueError:
    pass

print('compute_gpa tests passed')
