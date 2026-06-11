# User Service — manages user accounts
# Problem: This file duplicates utility functions found in other services

import re
import uuid
from datetime import datetime
from dataclasses import dataclass


def format_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")


def validate_email(email: str) -> bool:
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return bool(re.match(pattern, email))


def format_price(cents: int) -> str:
    return f"${cents / 100:.2f}"


@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: datetime
    balance: int  # in cents


def create_user(name: str, email: str) -> User:
    if not validate_email(email):
        raise ValueError(f"Invalid email: {email}")
    return User(
        id=uuid.uuid4().hex[:9],
        name=name,
        email=email,
        created_at=datetime.now(),
        balance=0,
    )


def get_user_summary(user: User) -> str:
    return (
        f"{user.name} ({user.email}) — "
        f"Joined: {format_date(user.created_at)} — "
        f"Balance: {format_price(user.balance)}"
    )
