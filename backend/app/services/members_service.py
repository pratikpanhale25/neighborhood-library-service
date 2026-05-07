"""Member use cases."""

from __future__ import annotations

from datetime import datetime, timezone

from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import Member
from app.services.exceptions import MemberNotFoundError, ValidationError
from app.services.pagination import decode_offset, next_offset_token
from app.services.validators import ensure_uuid

_MAX_PAGE = 200
_DEFAULT_PAGE = 50
_MAX_STR = 500


def _require_non_empty(s: str, field: str) -> str:
    """Validate required member text fields."""
    t = (s or "").strip()
    if not t:
        raise ValidationError(f"{field} is required", code="validation")
    if len(t) > _MAX_STR:
        raise ValidationError(f"{field} is too long", code="validation")
    return t


def create_member(
    session: Session,
    *,
    full_name: str,
    email: str,
    phone: str,
    address: str,
) -> Member:
    """Create a member record with uniqueness checks."""
    name = _require_non_empty(full_name, "full_name")
    em = _require_non_empty(email, "email")
    ph = _require_non_empty(phone, "phone")
    addr = (address or "").strip() or None
    now = datetime.now(timezone.utc)
    m = Member(
        full_name=name,
        email=em,
        phone=ph,
        address=addr,
        created_at=now,
        updated_at=now,
    )
    session.add(m)
    try:
        session.flush()
    except IntegrityError as exc:
        raise ValidationError("email already exists", code="duplicate_email") from exc
    return m


def update_member(
    session: Session,
    *,
    member_id: str,
    full_name: str,
    email: str,
    phone: str,
    address: str,
) -> Member:
    """Update an existing member and enforce email uniqueness."""
    mid = ensure_uuid("member_id", member_id)
    name = _require_non_empty(full_name, "full_name")
    em = _require_non_empty(email, "email")
    ph = _require_non_empty(phone, "phone")
    addr = (address or "").strip() or None
    m = session.get(Member, mid)
    if m is None:
        raise MemberNotFoundError(f"member not found: {member_id}", code="member_not_found")
    m.full_name = name
    m.email = em
    m.phone = ph
    m.address = addr
    m.updated_at = datetime.now(timezone.utc)
    try:
        session.flush()
    except IntegrityError as exc:
        raise ValidationError("email already exists", code="duplicate_email") from exc
    return m


def get_member(session: Session, *, member_id: str) -> Member:
    """Fetch one member by id."""
    mid = ensure_uuid("member_id", member_id)
    m = session.get(Member, mid)
    if m is None:
        raise MemberNotFoundError(f"member not found: {member_id}", code="member_not_found")
    return m


def list_members(session: Session, *, page_size: int, page_token: str) -> Tuple[List[Member], str]:
    """Return paginated members and next-page token."""
    try:
        offset = decode_offset(page_token)
    except ValueError as exc:
        raise ValidationError(str(exc), code="validation") from exc
    limit = page_size if page_size > 0 else _DEFAULT_PAGE
    limit = min(limit, _MAX_PAGE)
    q = (
        select(Member)
        .order_by(Member.created_at.asc(), Member.id.asc())
        .offset(offset)
        .limit(limit + 1)
    )
    rows = list(session.scalars(q).all())
    has_more = len(rows) > limit
    rows = rows[:limit]
    return rows, next_offset_token(offset, len(rows), has_more)
