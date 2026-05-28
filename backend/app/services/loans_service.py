"""Borrowing, returns, overdue listing, and fines integration."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.entities import Fine, Loan
from app.db.repositories import loans_repo
from app.services import fine_policy
from app.services.exceptions import (
    BookAlreadyOnLoanError,
    BookNotFoundError,
    InvalidReturnError,
    LoanNotFoundError,
    MemberNotFoundError,
    NoCopiesAvailableError,
    ValidationError,
)
from app.services.pagination import decode_offset, next_offset_token
from app.services.proto_enum_maps import loan_filter_proto_to_sql
from app.services.validators import ensure_uuid
from app.utils import timeutil

_MAX_PAGE = 200
_DEFAULT_PAGE = 50


def loan_display_status(loan: Loan, reference_time: datetime) -> str:
    """BORROWED / OVERDUE / RETURNED for API and gRPC."""
    if loan.returned_at is not None:
        return "RETURNED"
    if loan.due_at is not None and loan.due_at < reference_time:
        return "OVERDUE"
    return "BORROWED"


def loan_overdue_flags(loan: Loan, reference_time: datetime) -> Tuple[bool, int]:
    """Compute overdue boolean and late-day count for a loan."""
    if loan.returned_at is not None:
        return False, 0
    if loan.due_at is None:
        return False, 0
    days_late = fine_policy.calendar_days_late(loan.due_at, reference_time)
    if days_late <= 0:
        return False, 0
    return True, days_late


def borrow_book(
    session: Session,
    settings: Settings,
    *,
    member_id: str,
    book_id: str,
    due_at_explicit: Optional[datetime],
    loan_period_days: Optional[int],
) -> Loan:
    """Create a new active loan and decrement available copies."""
    if not (member_id or "").strip() or not (book_id or "").strip():
        raise ValidationError("member_id and book_id are required", code="validation")
    mid = ensure_uuid("member_id", member_id)
    bid = ensure_uuid("book_id", book_id)

    member = loans_repo.fetch_member(session, mid)
    if member is None:
        raise MemberNotFoundError(f"member not found: {member_id}", code="member_not_found")

    book = loans_repo.fetch_book_for_update(session, bid)
    if book is None:
        raise BookNotFoundError(f"book not found: {book_id}", code="book_not_found")

    if book.available_copies < 1:
        raise NoCopiesAvailableError("no copies available to borrow", code="no_copies")

    existing = loans_repo.find_active_loan(session, mid, bid)
    if existing is not None:
        raise BookAlreadyOnLoanError(
            "member already has an active borrow for this book",
            code="duplicate_active_borrow",
        )

    borrowed_at = timeutil.utc_now()
    try:
        due_at = fine_policy.resolve_due_at(
            borrowed_at,
            explicit_due=due_at_explicit,
            loan_period_days=loan_period_days,
            default_period_days=settings.default_loan_period_days,
        )
    except ValueError as exc:
        raise ValidationError(str(exc), code="validation") from exc

    loan = Loan(
        book_id=bid,
        member_id=mid,
        borrowed_at=borrowed_at,
        due_at=due_at,
        returned_at=None,
        status="BORROWED",
    )
    book.available_copies -= 1
    book.updated_at = borrowed_at
    session.add(loan)
    try:
        session.flush()
    except IntegrityError as exc:
        raise BookAlreadyOnLoanError(
            "member already has an active borrow for this book",
            code="duplicate_active_borrow",
        ) from exc
    return loan


def return_book(
    session: Session,
    settings: Settings,
    *,
    loan_id: str,
    member_id: str,
    book_id: str,
) -> Tuple[Loan, Optional[Fine]]:
    """Close an active loan, restore inventory, and optionally create a fine."""
    loan_id = (loan_id or "").strip()
    member_id_s = (member_id or "").strip()
    book_id_s = (book_id or "").strip()

    target: Optional[Loan] = None
    if loan_id:
        if member_id_s or book_id_s:
            raise ValidationError(
                "use either loan_id or member_id+book_id, not both", code="validation"
            )
        lid = ensure_uuid("loan_id", loan_id)
        # Serialize concurrent returns on the same loan (inventory + fine correctness).
        target = loans_repo.fetch_loan_by_id_for_update(session, lid)
        if target is None:
            raise LoanNotFoundError(f"loan not found: {loan_id}", code="loan_not_found")
        if target.returned_at is not None:
            raise InvalidReturnError("loan already returned", code="already_returned")
    else:
        if not member_id_s or not book_id_s:
            raise ValidationError(
                "loan_id or (member_id and book_id) is required", code="validation"
            )
        mid = ensure_uuid("member_id", member_id_s)
        bid = ensure_uuid("book_id", book_id_s)
        target = loans_repo.fetch_active_loan_member_book_for_update(session, mid, bid)
        if target is None:
            raise LoanNotFoundError("no active loan for member and book", code="loan_not_found")

    returned_at = timeutil.utc_now()
    book = loans_repo.fetch_book_for_update_by_id(session, target.book_id)
    target.returned_at = returned_at
    target.status = "RETURNED"
    book.available_copies += 1
    book.updated_at = returned_at

    created_fine: Optional[Fine] = None
    if (
        target.due_at is not None
        and target.returned_at is not None
        and target.returned_at > target.due_at
    ):
        raw_late = fine_policy.calendar_days_late(target.due_at, target.returned_at)
        billable = fine_policy.billable_overdue_days(raw_late, settings.fine_grace_days)
        amount = fine_policy.fine_amount_cents(billable, cents_per_day=settings.fine_cents_per_day)
        if amount > 0:
            existing_pending = session.execute(
                select(Fine).where(
                    and_(Fine.loan_id == target.id, Fine.status == "pending")
                )
            ).scalar_one_or_none()
            if existing_pending is not None:
                created_fine = existing_pending
            else:
                fine = Fine(
                    loan_id=target.id,
                    member_id=target.member_id,
                    amount_cents=amount,
                    currency=settings.fine_currency_code,
                    status="pending",
                    reason="overdue",
                    created_at=returned_at,
                )
                session.add(fine)
                session.flush()
                created_fine = fine

    return target, created_fine


def list_loans(
    session: Session,
    *,
    member_id: str,
    book_id: str,
    filter_enum: int,
    page_size: int,
    page_token: str,
) -> Tuple[List[Loan], str]:
    """List loans with filters and cursor pagination."""
    try:
        offset = decode_offset(page_token)
    except ValueError as exc:
        raise ValidationError(str(exc), code="validation") from exc

    m_raw = (member_id or "").strip() or None
    b_raw = (book_id or "").strip() or None
    # Single parse per id avoids redundant validation and keeps SQL params identical (review).
    mid_uuid: Optional[uuid.UUID] = None
    if m_raw is not None:
        mid_uuid = ensure_uuid("member_id", m_raw)
    bid_uuid: Optional[uuid.UUID] = None
    if b_raw is not None:
        bid_uuid = ensure_uuid("book_id", b_raw)

    limit = page_size if page_size > 0 else _DEFAULT_PAGE
    limit = min(limit, _MAX_PAGE)
    lf = loan_filter_proto_to_sql(filter_enum)
    now_utc = timeutil.utc_now() if lf == "overdue" else None

    conds = []
    if mid_uuid is not None:
        conds.append(Loan.member_id == mid_uuid)
    if bid_uuid is not None:
        conds.append(Loan.book_id == bid_uuid)
    if lf == "active":
        conds.append(Loan.returned_at.is_(None))
    elif lf == "returned":
        conds.append(Loan.returned_at.is_not(None))
    elif lf == "overdue":
        assert now_utc is not None
        conds.append(Loan.returned_at.is_(None))
        conds.append(Loan.due_at.is_not(None))
        conds.append(Loan.due_at < now_utc)
    rows = loans_repo.list_loans_page(session, where_conds=conds, offset=offset, limit_plus_one=limit + 1)
    has_more = len(rows) > limit
    rows = rows[:limit]
    return rows, next_offset_token(offset, len(rows), has_more)


def list_active_loans_for_member(session: Session, *, member_id: str) -> List[Loan]:
    """Return currently active loans for one member."""
    mid = ensure_uuid("member_id", member_id)
    return loans_repo.list_active_loans_for_member(session, mid)
