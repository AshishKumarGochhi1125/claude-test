# Report Service — generates summary reports
# Problem: This file duplicates utility functions found in other services

import re
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
class ReportConfig:
    title: str
    start_date: datetime
    end_date: datetime
    recipient_email: str
    total_revenue: int  # in cents


def generate_report(config: ReportConfig) -> str:
    if not validate_email(config.recipient_email):
        raise ValueError(f"Invalid recipient email: {config.recipient_email}")

    lines = [
        f"Report: {config.title}",
        f"Period: {format_date(config.start_date)} to {format_date(config.end_date)}",
        f"Revenue: {format_price(config.total_revenue)}",
        f"Recipient: {config.recipient_email}",
    ]

    return "\n".join(lines)
