"""Book catalog use cases."""

from __future__ import annotations

from datetime import datetime, timezone

from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import Book
from app.services.exceptions import BookNotFoundError, ValidationError
from app.services.pagination import decode_offset, next_offset_token
from app.services.validators import ensure_uuid

_MAX_PAGE = 200
_DEFAULT_PAGE = 50
_MAX_STR = 2000
_MAX_TITLE = 512


def _require_non_empty(s: str, field: str) -> str:
    """Validate required text fields and normalize whitespace."""
    t = (s or "").strip()
    if not t:
        raise ValidationError(f"{field} is required", code="validation")
    if len(t) > _MAX_STR:
        raise ValidationError(f"{field} is too long", code="validation")
    return t


def _validate_title_author(title: str, author: str) -> tuple[str, str]:
    """Apply shared validation rules for book title/author."""
    t = _require_non_empty(title, "title")
    a = _require_non_empty(author, "author")
    if len(t) > _MAX_TITLE:
        raise ValidationError("title is too long", code="validation")
    return t, a


def create_book(
    session: Session,
    *,
    title: str,
    author: str,
    isbn: str,
    publication_year: Optional[int],
    total_copies: int,
) -> Book:
    """Create a book with validated fields and initial inventory."""
    t, a = _validate_title_author(title, author)
    isbn_clean = _require_non_empty(isbn, "isbn")
    if len(isbn_clean) > 32:
        raise ValidationError("isbn is too long", code="validation")
    year: Optional[int] = publication_year if publication_year and publication_year > 0 else None
    if year is not None and (year < 1000 or year > 3000):
        raise ValidationError("publication_year is out of range", code="validation")
    n = total_copies if total_copies and total_copies > 0 else 1
    if n > 10_000:
        raise ValidationError("total_copies out of range", code="validation")
    now = datetime.now(timezone.utc)
    book = Book(
        title=t,
        author=a,
        isbn=isbn_clean,
        publication_year=year,
        total_copies=n,
        available_copies=n,
        created_at=now,
        updated_at=now,
    )
    session.add(book)
    try:
        session.flush()
    except IntegrityError as exc:
        raise ValidationError("isbn already exists", code="duplicate_isbn") from exc
    return book


def update_book(
    session: Session,
    *,
    book_id: str,
    title: str,
    author: str,
    isbn: str,
    publication_year: Optional[int],
    total_copies: Optional[int],
) -> Book:
    """Update book fields and keep inventory math consistent."""
    bid = ensure_uuid("book_id", book_id)
    t, a = _validate_title_author(title, author)
    isbn_clean = _require_non_empty(isbn, "isbn")
    year: Optional[int] = publication_year if publication_year and publication_year > 0 else None
    if year is not None and (year < 1000 or year > 3000):
        raise ValidationError("publication_year is out of range", code="validation")
    book = session.get(Book, bid)
    if book is None:
        raise BookNotFoundError(f"book not found: {book_id}", code="book_not_found")
    on_loan = book.total_copies - book.available_copies
    new_total = book.total_copies if total_copies is None else total_copies
    if new_total is not None and new_total < 1:
        raise ValidationError("total_copies must be at least 1", code="validation")
    if new_total is not None and new_total < on_loan:
        raise ValidationError(
            "total_copies cannot be less than number of copies currently borrowed",
            code="validation",
        )
    book.title = t
    book.author = a
    book.isbn = isbn_clean
    book.publication_year = year
    book.updated_at = datetime.now(timezone.utc)
    if new_total is not None:
        book.total_copies = new_total
        book.available_copies = new_total - on_loan
    try:
        session.flush()
    except IntegrityError as exc:
        raise ValidationError("isbn already exists", code="duplicate_isbn") from exc
    return book


def get_book(session: Session, *, book_id: str) -> Book:
    """Fetch a single book or raise a domain not-found error."""
    bid = ensure_uuid("book_id", book_id)
    book = session.get(Book, bid)
    if book is None:
        raise BookNotFoundError(f"book not found: {book_id}", code="book_not_found")
    return book


def list_books(session: Session, *, page_size: int, page_token: str) -> Tuple[List[Book], str]:
    """Return paginated books with an encoded next-page token."""
    try:
        offset = decode_offset(page_token)
    except ValueError as exc:
        raise ValidationError(str(exc), code="validation") from exc
    limit = page_size if page_size > 0 else _DEFAULT_PAGE
    limit = min(limit, _MAX_PAGE)
    q = (
        select(Book)
        .order_by(Book.created_at.asc(), Book.id.asc())
        .offset(offset)
        .limit(limit + 1)
    )
    rows = list(session.scalars(q).all())
    has_more = len(rows) > limit
    rows = rows[:limit]
    return rows, next_offset_token(offset, len(rows), has_more)
