"""Fines listing and staff actions."""

from __future__ import annotations

from datetime import datetime, timezone

from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Fine
from app.services.exceptions import FineNotFoundError, InvalidFineStateError, ValidationError
from app.services.pagination import decode_offset, next_offset_token
from app.services.validators import ensure_uuid

_MAX_PAGE = 200
_DEFAULT_PAGE = 50

FineStatusSQL = str  # pending | paid | waived | any


def _utc_now() -> datetime:
    """Return current UTC time for fine state transitions."""
    return datetime.now(timezone.utc)


def _proto_fine_status_to_sql(filter_val: int) -> str:
    """Map enum-like filter values to persisted fine status labels."""
    if filter_val == 1:
        return "pending"
    if filter_val == 2:
        return "paid"
    if filter_val == 3:
        return "waived"
    if filter_val == 4:
        return "any"
    return "any"


def list_fines(
    session: Session,
    *,
    member_id: str,
    status_filter_enum: int,
    page_size: int,
    page_token: str,
) -> Tuple[List[Fine], str]:
    """List fines with optional member/status filtering."""
    try:
        offset = decode_offset(page_token)
    except ValueError as exc:
        raise ValidationError(str(exc), code="validation") from exc

    m = (member_id or "").strip() or None
    if m is not None:
        ensure_uuid("member_id", m)

    limit = page_size if page_size > 0 else _DEFAULT_PAGE
    limit = min(limit, _MAX_PAGE)
    st = _proto_fine_status_to_sql(status_filter_enum)

    q = select(Fine)
    conds = []
    if m is not None:
        conds.append(Fine.member_id == ensure_uuid("member_id", m))
    if st != "any":
        conds.append(Fine.status == st)
    if conds:
        q = q.where(*conds)
    q = q.order_by(Fine.created_at.desc(), Fine.id.desc()).offset(offset).limit(limit + 1)
    rows = list(session.scalars(q).all())
    has_more = len(rows) > limit
    rows = rows[:limit]
    return rows, next_offset_token(offset, len(rows), has_more)


def get_fine(session: Session, *, fine_id: str) -> Fine:
    """Fetch a fine by id."""
    fid = ensure_uuid("fine_id", fine_id)
    row = session.get(Fine, fid)
    if row is None:
        raise FineNotFoundError(f"fine not found: {fine_id}", code="fine_not_found")
    return row


def pay_fine(session: Session, *, fine_id: str, notes: str) -> Fine:
    """Transition a pending fine to paid state."""
    fid = ensure_uuid("fine_id", fine_id)
    existing = session.get(Fine, fid)
    if existing is None:
        raise FineNotFoundError(f"fine not found: {fine_id}", code="fine_not_found")
    if existing.status != "pending":
        raise InvalidFineStateError(f"fine is not pending: {fine_id}", code="invalid_fine_state")
    now = _utc_now()
    n = notes or ""
    existing.status = "paid"
    existing.resolved_at = now
    if n:
        existing.notes = n if not existing.notes else f"{existing.notes}\n{n}"
    session.flush()
    return existing


def waive_fine(session: Session, *, fine_id: str, notes: str) -> Fine:
    """Transition a pending fine to waived state."""
    fid = ensure_uuid("fine_id", fine_id)
    existing = session.get(Fine, fid)
    if existing is None:
        raise FineNotFoundError(f"fine not found: {fine_id}", code="fine_not_found")
    if existing.status != "pending":
        raise InvalidFineStateError(f"fine is not pending: {fine_id}", code="invalid_fine_state")
    now = _utc_now()
    n = notes or ""
    existing.status = "waived"
    existing.resolved_at = now
    if n:
        existing.notes = n if not existing.notes else f"{existing.notes}\n{n}"
    session.flush()
    return existing
