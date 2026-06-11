import pytest
from user_service import create_user, get_user_summary


def test_create_user_with_valid_email():
    user = create_user("Alice", "alice@example.com")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.balance == 0


def test_create_user_with_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        create_user("Bob", "not-an-email")


def test_get_user_summary():
    user = create_user("Alice", "alice@example.com")
    summary = get_user_summary(user)
    assert "Alice" in summary
    assert "alice@example.com" in summary
    assert "$0.00" in summary
