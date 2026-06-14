import pytest
from calculator import add, subtract, multiply, divide, DivisionByZeroError


class TestAdd:
    def test_adds_two_positive_numbers(self):
        assert add(2, 3) == 5

    def test_adds_negative_numbers(self):
        assert add(-1, -2) == -3

    def test_adds_zero(self):
        assert add(5, 0) == 5


class TestSubtract:
    def test_subtracts_two_numbers(self):
        assert subtract(10, 3) == 7

    def test_handles_negative_results(self):
        assert subtract(3, 10) == -7


class TestMultiply:
    def test_multiplies_two_numbers(self):
        assert multiply(4, 5) == 20

    def test_multiplies_by_zero(self):
        assert multiply(100, 0) == 0

    def test_multiplies_negative_numbers(self):
        assert multiply(-3, 4) == -12


class TestDivide:
    def test_divides_two_numbers(self):
        assert divide(10, 2) == 5

    def test_handles_decimal_results(self):
        assert divide(7, 2) == 3.5

    def test_divides_negative_numbers(self):
        assert divide(-10, 2) == -5

    # THIS TEST FAILS — divide() raises generic Exception, not DivisionByZeroError
    def test_raises_division_by_zero_error(self):
        with pytest.raises(DivisionByZeroError):
            divide(5, 0)

    # THIS TEST ALSO FAILS — same root cause
    def test_raises_division_by_zero_error_with_message(self):
        with pytest.raises(DivisionByZeroError, match="Cannot divide by zero"):
            divide(0, 0)
