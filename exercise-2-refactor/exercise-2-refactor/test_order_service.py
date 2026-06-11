from datetime import datetime
from order_service import OrderItem, Order, calculate_order_total, get_order_summary


sample_order = Order(
    id="ORD-001",
    items=[
        OrderItem(name="Widget", quantity=2, price_in_cents=1500),
        OrderItem(name="Gadget", quantity=1, price_in_cents=3000),
    ],
    created_at=datetime(2025, 1, 15),
    status="pending",
)


def test_calculate_order_total():
    assert calculate_order_total(sample_order.items) == 6000


def test_get_order_summary():
    summary = get_order_summary(sample_order)
    assert "ORD-001" in summary
    assert "$60.00" in summary
    assert "pending" in summary
