# Order Service — manages customer orders
# Problem: This file duplicates utility functions found in other services

from datetime import datetime
from dataclasses import dataclass, field


def format_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")


def format_price(cents: int) -> str:
    return f"${cents / 100:.2f}"


@dataclass
class OrderItem:
    name: str
    quantity: int
    price_in_cents: int


@dataclass
class Order:
    id: str
    items: list[OrderItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, shipped, delivered


def calculate_order_total(items: list[OrderItem]) -> int:
    return sum(item.price_in_cents * item.quantity for item in items)


def get_order_summary(order: Order) -> str:
    total = calculate_order_total(order.items)
    return (
        f"Order {order.id} — {format_date(order.created_at)} — "
        f"{len(order.items)} items — Total: {format_price(total)} — {order.status}"
    )
