"""Fine row reads (ORM only)."""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.entities import Fine


def fetch_by_id(session: Session, fine_id: uuid.UUID) -> Optional[Fine]:
    return session.get(Fine, fine_id)


def list_fines_page(
    session: Session,
    *,
    where_conds: list,
    offset: int,
    limit_plus_one: int,
) -> List[Fine]:
    q = select(Fine)
    if where_conds:
        q = q.where(*where_conds)
    q = q.order_by(Fine.created_at.desc(), Fine.id.desc()).offset(offset).limit(limit_plus_one)
    return list(session.scalars(q).all())
