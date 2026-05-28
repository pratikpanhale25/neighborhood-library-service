"""Book persistence helpers (SQLAlchemy only; business rules stay in services).

Code review: isolate ORM access so services stay use-case focused and easier to test.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.entities import Book


def fetch_by_id(session: Session, book_id: uuid.UUID) -> Optional[Book]:
    return session.get(Book, book_id)


def list_page(
    session: Session,
    *,
    offset: int,
    limit_plus_one: int,
    query: Optional[str] = None,
    author: Optional[str] = None,
) -> List[Book]:
    """Return up to ``limit_plus_one`` rows (caller uses +1 to detect ``has_more``)."""
    q = select(Book)
    conds = []
    qtext = (query or "").strip()
    if qtext:
        pat = f"%{qtext}%"
        # Broad catalog search for staff/patron lookup (review: list filter support).
        conds.append(or_(Book.title.ilike(pat), Book.author.ilike(pat), Book.isbn.ilike(pat)))
    auth = (author or "").strip()
    if auth:
        conds.append(Book.author.ilike(f"%{auth}%"))
    if conds:
        q = q.where(*conds)
    q = q.order_by(Book.created_at.asc(), Book.id.asc()).offset(offset).limit(limit_plus_one)
    return list(session.scalars(q).all())
