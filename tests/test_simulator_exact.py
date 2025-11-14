from app.simulator import generate_grade_combinations, find_worst_scenarios
from app.utils import truncate

CUS = [3, 3, 3, 3, 4, 4, 4]
TARGET = 4.29


def assert_no_F_and_at_target(results, target):
    assert results is not None
    for grades, gpa in results:
        # no F present
        assert 'F' not in grades
        # truncated to 2 decimals must equal target truncated (exact-match semantics)
        assert truncate(gpa, 2) == round(target, 2)
        # also ensure not exceeding the target
        assert gpa <= target + 1e-9


def test_exact_match_returns_only_target_combos():
    results = generate_grade_combinations(7, CUS, TARGET, exact_match=True, max_results=50)
    # expect at least one exact match exists for the sample
    assert len(results) > 0
    assert len(results) <= 50
    assert_no_F_and_at_target(results, TARGET)


def test_find_worst_scenarios_exact_match():
    results = find_worst_scenarios(7, CUS, TARGET, count=50, exact_match=True, allow_A_if_needed=True)
    assert len(results) > 0
    assert len(results) <= 50
    assert_no_F_and_at_target(results, TARGET)


def test_default_generation_does_not_exceed_target():
    # default (non-exact) should not produce GPA > target for returned results
    results = generate_grade_combinations(7, CUS, TARGET, exact_match=False, max_results=30)
    # it's acceptable to return zero results, but any returned must not exceed TARGET
    for grades, gpa in results:
        assert 'F' not in grades
        assert gpa <= TARGET + 1e-9


if __name__ == '__main__':
    # Provide a simple runner so this file can be executed directly without pytest installed
    try:
        test_exact_match_returns_only_target_combos()
        test_find_worst_scenarios_exact_match()
        test_default_generation_does_not_exceed_target()
        print('ALL_TESTS_OK')
    except AssertionError as e:
        print('TEST_FAILED', e)
        raise
