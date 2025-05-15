import pytest

from tools import is_excited_pattern, is_valid, calculate_num_balls


@pytest.mark.parametrize(
    "pattern, is_pattern_valid",
    [
        pytest.param([5, 3, 1], True),
        pytest.param([7, 7, 7, 7, 2], True),
        pytest.param([5, 1, 3], False),
    ],
)
def test_is_valid(pattern, is_pattern_valid):
    assert is_valid(pattern) == is_pattern_valid


@pytest.mark.parametrize(
    "pattern, is_excited",
    [
        pytest.param([5, 3, 1], False),
        pytest.param([4, 4, 9, 9, 9], True),
        pytest.param([11, 9, 1], True),
    ],
)
def test_is_excited_pattern(pattern, is_excited):
    assert is_excited_pattern(pattern) == is_excited

@pytest.mark.parametrize(
    "pattern, num_of_balls",
    [
        pytest.param([], None),
        pytest.param([7, 7, 7, 7, 2], 6),
        pytest.param([5, 1, 3], 3),
    ],
)
def test_calculate_num_balls(pattern, num_of_balls):
    assert calculate_num_balls(pattern) == num_of_balls