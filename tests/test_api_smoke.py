from app.gpa_calculator import compute_gpa
from app.cgpa_calculator import update_cgpa
from app.simulator import generate_grade_combinations

def test_compute_gpa():
    assert compute_gpa([(3,'A'),(3,'B+'),(4,'B')]) >= 0

def test_update_cgpa():
    assert update_cgpa(4.0, 40, 4.2, 20) > 0

def test_simulator():
    res = generate_grade_combinations(3, [3,3,3], 4.0)
    assert isinstance(res, list)

if __name__ == '__main__':
    test_compute_gpa()
    test_update_cgpa()
    test_simulator()
    print('smoke tests ok')
