"""Helpers for ``google.protobuf.Timestamp`` and domain datetimes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from google.protobuf.timestamp_pb2 import Timestamp


def datetime_to_pb(dt: Optional[datetime]) -> Optional[Timestamp]:
    """Convert datetime to protobuf Timestamp."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts


def pb_to_datetime(ts: Optional[Timestamp]) -> Optional[datetime]:
    """Convert protobuf Timestamp to UTC datetime."""
    if ts is None:
        return None
    if ts.seconds == 0 and ts.nanos == 0:
        return None
    return ts.ToDatetime(tzinfo=timezone.utc)
