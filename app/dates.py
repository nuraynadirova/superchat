"""Builds a small calendar so the LLM never has to compute weekdays itself."""
from datetime import date, timedelta

from .config import settings


def calendar_text(days: int = 14) -> str:
    today = date.fromisoformat(settings.reference_date)
    lines = []
    for i in range(days):
        d = today + timedelta(days=i)
        tag = " (TODAY)" if i == 0 else " (tomorrow)" if i == 1 else ""
        lines.append(f"{d.strftime('%A')} = {d.isoformat()}{tag}")
    return "\n".join(lines)


def today_iso() -> str:
    return settings.reference_date
