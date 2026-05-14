"""Book REST routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.library import BookCreate, BookRead, BookUpdate, PaginatedBooks
from app.services import books_service


router = APIRouter(prefix="/books", tags=["books"])


@router.post("", response_model=BookRead, status_code=201)
def create_book(body: BookCreate, db: Session = Depends(get_db)) -> BookRead:
    """Create a new book catalog record."""
    row = books_service.create_book(
        db,
        title=body.title,
        author=body.author,
        isbn=body.isbn,
        publication_year=body.publication_year,
        total_copies=body.total_copies,
    )
    return BookRead.model_validate(row)


@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: str, body: BookUpdate, db: Session = Depends(get_db)) -> BookRead:
    """Update an existing book by id."""
    row = books_service.update_book(
        db,
        book_id=book_id,
        title=body.title,
        author=body.author,
        isbn=body.isbn,
        publication_year=body.publication_year,
        total_copies=body.total_copies,
    )
    return BookRead.model_validate(row)


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: str, db: Session = Depends(get_db)) -> BookRead:
    """Fetch one book by id."""
    row = books_service.get_book(db, book_id=book_id)
    return BookRead.model_validate(row)


@router.get("", response_model=PaginatedBooks)
def list_books(
    db: Session = Depends(get_db),
    page_size: int = Query(default=50, ge=1, le=200),
    page_token: str = Query(default=""),
    query: Optional[str] = Query(default=None, description="Substring match on title, author, or ISBN"),
    author: Optional[str] = Query(default=None, description="Additional filter on author only"),
) -> PaginatedBooks:
    """List books with cursor-style pagination."""
    rows, tok = books_service.list_books(
        db,
        page_size=page_size,
        page_token=page_token,
        query=query,
        author=author,
    )
    return PaginatedBooks(
        items=[BookRead.model_validate(r) for r in rows],
        next_page_token=tok,
    )
