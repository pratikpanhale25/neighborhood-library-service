"""Tests for shared datetime helpers."""

from __future__ import annotations

from datetime import timezone

from app.utils import timeutil


def test_utc_now_is_timezone_aware() -> None:
    """Single clock helper must stay UTC-aware so loan/fine math stays consistent (review)."""
    dt = timeutil.utc_now()
    assert dt.tzinfo == timezone.utc
