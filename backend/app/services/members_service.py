"""Member use cases."""

from __future__ import annotations

from typing import List, Optional, Set, Tuple

from google.protobuf.field_mask_pb2 import FieldMask
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.entities import Member
from app.db.repositories import members_repo
from app.services.exceptions import MemberNotFoundError, ValidationError
from app.services.pagination import decode_offset, next_offset_token
from app.services.validators import ensure_uuid
from app.utils import timeutil

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
    now = timeutil.utc_now()
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
    update_mask: Optional[FieldMask] = None,
) -> Member:
    """Update an existing member and enforce email uniqueness."""
    mid = ensure_uuid("member_id", member_id)
    m = members_repo.fetch_by_id(session, mid)
    if m is None:
        raise MemberNotFoundError(f"member not found: {member_id}", code="member_not_found")

    paths: Set[str] = set(update_mask.paths) if update_mask and update_mask.paths else set()
    if not paths:
        name = _require_non_empty(full_name, "full_name")
        em = _require_non_empty(email, "email")
        ph = _require_non_empty(phone, "phone")
        addr = (address or "").strip() or None
        m.full_name = name
        m.email = em
        m.phone = ph
        m.address = addr
        m.updated_at = timeutil.utc_now()
    else:
        if "full_name" in paths:
            m.full_name = _require_non_empty(full_name, "full_name")
        if "email" in paths:
            m.email = _require_non_empty(email, "email")
        if "phone" in paths:
            m.phone = _require_non_empty(phone, "phone")
        if "address" in paths:
            m.address = (address or "").strip() or None
        m.updated_at = timeutil.utc_now()
    try:
        session.flush()
    except IntegrityError as exc:
        raise ValidationError("email already exists", code="duplicate_email") from exc
    return m


def get_member(session: Session, *, member_id: str) -> Member:
    """Fetch one member by id."""
    mid = ensure_uuid("member_id", member_id)
    m = members_repo.fetch_by_id(session, mid)
    if m is None:
        raise MemberNotFoundError(f"member not found: {member_id}", code="member_not_found")
    return m


def list_members(
    session: Session,
    *,
    page_size: int,
    page_token: str,
    query: Optional[str] = None,
) -> Tuple[List[Member], str]:
    """Return paginated members and next-page token."""
    try:
        offset = decode_offset(page_token)
    except ValueError as exc:
        raise ValidationError(str(exc), code="validation") from exc
    limit = page_size if page_size > 0 else _DEFAULT_PAGE
    limit = min(limit, _MAX_PAGE)
    rows = members_repo.list_page(session, offset=offset, limit_plus_one=limit + 1, query=query)
    has_more = len(rows) > limit
    rows = rows[:limit]
    return rows, next_offset_token(offset, len(rows), has_more)
