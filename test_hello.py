from hello import greet


def test_greet_basic():
    assert greet("Ada") == "Hello, Ada! Welcome to the workshop."


def test_greet_empty_string():
    assert greet("") == "Hello, ! Welcome to the workshop."


def test_greet_returns_str():
    assert isinstance(greet("Bob"), str)
