"""Offset pagination helpers (opaque page tokens)."""

from __future__ import annotations

import base64
import struct


def decode_offset(page_token: str) -> int:
    """
    Decode an opaque page token to a non-negative offset.

    Raises:
        ValueError: If the token is invalid.
    """
    if not page_token:
        return 0
    try:
        raw = base64.urlsafe_b64decode(page_token.encode("ascii") + b"=" * (-len(page_token) % 4))
        (offset,) = struct.unpack(">Q", raw)
        return int(offset)
    except Exception as exc:
        raise ValueError("invalid page_token") from exc


def next_offset_token(offset: int, page_len: int, has_more: bool) -> str:
    """Return the next opaque token, or empty string if no further pages."""
    if not has_more:
        return ""
    next_off = offset + page_len
    raw = struct.pack(">Q", next_off)
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
