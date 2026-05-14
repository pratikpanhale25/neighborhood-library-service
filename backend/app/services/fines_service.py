"""Fines listing and staff actions."""

from __future__ import annotations

import uuid
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.db.entities import Fine
from app.db.repositories import fines_repo
from app.services.exceptions import FineNotFoundError, InvalidFineStateError, ValidationError
from app.services.pagination import decode_offset, next_offset_token
from app.services.proto_enum_maps import fine_status_filter_proto_to_sql
from app.services.validators import ensure_uuid
from app.utils import timeutil

_MAX_PAGE = 200
_DEFAULT_PAGE = 50


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

    m_raw = (member_id or "").strip() or None
    # One UUID parse for validation + WHERE keeps behavior consistent (review).
    mid_uuid: Optional[uuid.UUID] = None
    if m_raw is not None:
        mid_uuid = ensure_uuid("member_id", m_raw)

    limit = page_size if page_size > 0 else _DEFAULT_PAGE
    limit = min(limit, _MAX_PAGE)
    st = fine_status_filter_proto_to_sql(status_filter_enum)

    conds = []
    if mid_uuid is not None:
        conds.append(Fine.member_id == mid_uuid)
    if st != "any":
        conds.append(Fine.status == st)
    rows = fines_repo.list_fines_page(session, where_conds=conds, offset=offset, limit_plus_one=limit + 1)
    has_more = len(rows) > limit
    rows = rows[:limit]
    return rows, next_offset_token(offset, len(rows), has_more)


def get_fine(session: Session, *, fine_id: str) -> Fine:
    """Fetch a fine by id."""
    fid = ensure_uuid("fine_id", fine_id)
    row = fines_repo.fetch_by_id(session, fid)
    if row is None:
        raise FineNotFoundError(f"fine not found: {fine_id}", code="fine_not_found")
    return row


def pay_fine(session: Session, *, fine_id: str, notes: str) -> Fine:
    """Transition a pending fine to paid state."""
    fid = ensure_uuid("fine_id", fine_id)
    existing = fines_repo.fetch_by_id(session, fid)
    if existing is None:
        raise FineNotFoundError(f"fine not found: {fine_id}", code="fine_not_found")
    if existing.status != "pending":
        raise InvalidFineStateError(f"fine is not pending: {fine_id}", code="invalid_fine_state")
    now = timeutil.utc_now()
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
    existing = fines_repo.fetch_by_id(session, fid)
    if existing is None:
        raise FineNotFoundError(f"fine not found: {fine_id}", code="fine_not_found")
    if existing.status != "pending":
        raise InvalidFineStateError(f"fine is not pending: {fine_id}", code="invalid_fine_state")
    now = timeutil.utc_now()
    n = notes or ""
    existing.status = "waived"
    existing.resolved_at = now
    if n:
        existing.notes = n if not existing.notes else f"{existing.notes}\n{n}"
    session.flush()
    return existing
