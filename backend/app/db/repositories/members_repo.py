"""Member persistence helpers (ORM only).

Code review: separate data access from member validation and uniqueness handling.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.entities import Member


def fetch_by_id(session: Session, member_id: uuid.UUID) -> Optional[Member]:
    return session.get(Member, member_id)


def list_page(
    session: Session,
    *,
    offset: int,
    limit_plus_one: int,
    query: Optional[str] = None,
) -> List[Member]:
    """Return up to ``limit_plus_one`` members for offset pagination."""
    q = select(Member)
    qtext = (query or "").strip()
    if qtext:
        pat = f"%{qtext}%"
        q = q.where(or_(Member.full_name.ilike(pat), Member.email.ilike(pat)))
    q = q.order_by(Member.created_at.asc(), Member.id.asc()).offset(offset).limit(limit_plus_one)
    return list(session.scalars(q).all())
