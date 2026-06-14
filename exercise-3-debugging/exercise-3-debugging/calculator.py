"""
Calculator module

A simple arithmetic library with add, subtract, multiply, and divide.

BUG: The divide function has a bug — it raises a generic Exception
instead of the custom DivisionByZeroError when dividing by zero.
The test suite catches this because it checks for the specific error type.
"""


class DivisionByZeroError(Exception):
    def __init__(self, message: str = "Cannot divide by zero"):
        super().__init__(message)


def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    """
    Divides a by b.
    Should raise DivisionByZeroError when b is 0.

    BUG: Currently raises generic Exception instead of DivisionByZeroError.
    """
    if b == 0:
        # BUG: This should be `raise DivisionByZeroError()`
        # but it raises a generic Exception instead
        raise Exception("Cannot divide by zero")
    return a / b
