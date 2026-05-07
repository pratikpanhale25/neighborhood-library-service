"""Pagination helpers."""

from __future__ import annotations

import pytest

from app.services.pagination import decode_offset, next_offset_token


def test_decode_offset_empty() -> None:
    assert decode_offset("") == 0


def test_decode_offset_invalid() -> None:
    with pytest.raises(ValueError):
        decode_offset("abc")


def test_next_token_roundtrip() -> None:
    tok = next_offset_token(0, 5, True)
    assert tok != ""
    assert decode_offset(tok) == 5
    assert next_offset_token(0, 5, False) == ""
