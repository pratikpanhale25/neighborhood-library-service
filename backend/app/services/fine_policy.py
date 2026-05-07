"""Pure functions for calendar-based overdue days and fine amounts (no I/O)."""

from __future__ import annotations

from typing import Optional

from datetime import datetime, timedelta, timezone


def utc_date(dt: datetime):
    """Return the calendar date of ``dt`` in UTC."""
    return dt.astimezone(timezone.utc).date()


def calendar_days_late(due_at: datetime, event_at: datetime) -> int:
    """Whole calendar days late when ``event_at`` is after the due calendar date."""
    d_due = utc_date(due_at)
    d_ev = utc_date(event_at)
    if d_ev <= d_due:
        return 0
    return (d_ev - d_due).days


def billable_overdue_days(raw_calendar_days_late: int, grace_days: int) -> int:
    """Days that contribute to billing after subtracting grace."""
    return max(0, raw_calendar_days_late - grace_days)


def fine_amount_cents(
    billable_days: int,
    *,
    cents_per_day: int,
) -> int:
    """Total fine in cents for billable overdue days."""
    if cents_per_day < 0:
        raise ValueError("cents_per_day must be non-negative")
    return max(0, billable_days * cents_per_day)


def resolve_due_at(
    borrowed_at: datetime,
    *,
    explicit_due: Optional[datetime],
    loan_period_days: Optional[int],
    default_period_days: int,
) -> datetime:
    """Compute loan due timestamp from borrow time and optional overrides."""
    if explicit_due is not None:
        due = explicit_due
    elif loan_period_days is not None and loan_period_days > 0:
        if loan_period_days > 3650:
            raise ValueError("loan_period_days out of range")
        due = borrowed_at + timedelta(days=loan_period_days)
    else:
        if default_period_days < 1 or default_period_days > 3650:
            raise ValueError("default_period_days out of range")
        due = borrowed_at + timedelta(days=default_period_days)

    if due <= borrowed_at:
        raise ValueError("due_at must be after borrowed_at")
    return due
