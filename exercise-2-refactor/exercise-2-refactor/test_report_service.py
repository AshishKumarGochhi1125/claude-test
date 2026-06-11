import pytest
from datetime import datetime
from report_service import ReportConfig, generate_report


def test_generate_report():
    report = generate_report(ReportConfig(
        title="Q1 Revenue",
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 3, 31),
        recipient_email="boss@example.com",
        total_revenue=150000,
    ))
    assert "Q1 Revenue" in report
    assert "2025-01-01" in report
    assert "$1500.00" in report


def test_generate_report_invalid_email():
    with pytest.raises(ValueError, match="Invalid recipient email"):
        generate_report(ReportConfig(
            title="Test",
            start_date=datetime.now(),
            end_date=datetime.now(),
            recipient_email="bad-email",
            total_revenue=0,
        ))
