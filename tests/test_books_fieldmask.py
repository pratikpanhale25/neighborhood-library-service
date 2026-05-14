"""FieldMask-driven partial updates (no DB)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from google.protobuf.field_mask_pb2 import FieldMask
from sqlalchemy.orm import Session

from app.db.entities import Book
from app.db.repositories import books_repo
from app.services.books_service import update_book
from app.services.exceptions import ValidationError


def test_update_book_partial_mask_only_changes_listed_columns() -> None:
    """gRPC FieldMask path: only masked columns mutate; others stay put (review)."""
    session = MagicMock(spec=Session)
    now = datetime.now(timezone.utc)
    book = Book(
        title="Old",
        author="Auth",
        isbn="111",
        publication_year=2000,
        total_copies=3,
        available_copies=3,
        created_at=now,
        updated_at=now,
    )
    book.id = UUID("00000000-0000-0000-0000-000000000001")

    with patch.object(books_repo, "fetch_by_id", return_value=book):
        mask = FieldMask()
        mask.paths.append("title")
        update_book(
            session,
            book_id=str(book.id),
            title="New",
            author="ignored",
            isbn="ignored",
            publication_year=1999,
            total_copies=1,
            update_mask=mask,
        )
    assert book.title == "New"
    assert book.author == "Auth"
    assert book.isbn == "111"


def test_update_book_empty_mask_still_validates_all_fields() -> None:
    """REST sends a full payload; empty mask must keep strict validation (backward compat)."""
    session = MagicMock(spec=Session)
    now = datetime.now(timezone.utc)
    book = Book(
        title="Old",
        author="Auth",
        isbn="111",
        publication_year=2000,
        total_copies=2,
        available_copies=2,
        created_at=now,
        updated_at=now,
    )
    book.id = UUID("00000000-0000-0000-0000-000000000001")

    with patch.object(books_repo, "fetch_by_id", return_value=book):
        with pytest.raises(ValidationError):
            update_book(
                session,
                book_id=str(book.id),
                title="",
                author="A",
                isbn="222",
                publication_year=None,
                total_copies=None,
                update_mask=None,
            )
