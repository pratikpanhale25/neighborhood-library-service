"""Unit tests for overdue day and fine amount helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.services import fine_policy


def test_calendar_days_late_same_day_not_late() -> None:
    due = datetime(2025, 6, 1, 23, 0, tzinfo=timezone.utc)
    ret = datetime(2025, 6, 1, 1, 0, tzinfo=timezone.utc)
    assert fine_policy.calendar_days_late(due, ret) == 0


def test_calendar_days_late_next_day() -> None:
    due = datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc)
    ret = datetime(2025, 6, 2, 12, 0, tzinfo=timezone.utc)
    assert fine_policy.calendar_days_late(due, ret) == 1


def test_billable_after_grace() -> None:
    assert fine_policy.billable_overdue_days(5, grace_days=2) == 3


def test_fine_amount() -> None:
    assert fine_policy.fine_amount_cents(3, cents_per_day=50) == 150


def test_resolve_due_explicit() -> None:
    borrowed = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    due = datetime(2025, 1, 10, 12, 0, tzinfo=timezone.utc)
    out = fine_policy.resolve_due_at(
        borrowed,
        explicit_due=due,
        loan_period_days=None,
        default_period_days=14,
    )
    assert out == due


def test_resolve_due_default_period() -> None:
    borrowed = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    out = fine_policy.resolve_due_at(
        borrowed,
        explicit_due=None,
        loan_period_days=None,
        default_period_days=14,
    )
    assert out == borrowed + timedelta(days=14)


def test_resolve_due_period_override() -> None:
    borrowed = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    out = fine_policy.resolve_due_at(
        borrowed,
        explicit_due=None,
        loan_period_days=7,
        default_period_days=14,
    )
    assert out == borrowed + timedelta(days=7)


def test_resolve_due_rejects_not_after_borrow() -> None:
    borrowed = datetime(2025, 1, 2, 12, 0, tzinfo=timezone.utc)
    due = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        fine_policy.resolve_due_at(
            borrowed,
            explicit_due=due,
            loan_period_days=None,
            default_period_days=14,
        )
