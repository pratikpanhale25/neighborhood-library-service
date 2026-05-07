"""Borrow / return / borrow-records REST routes."""

from __future__ import annotations

from datetime import datetime, timezone

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_settings
from app.core.config import Settings
from app.schemas.library import BorrowRecordRead, BorrowRequest, PaginatedBorrowRecords, ReturnRequest
from app.services import loans_service

router = APIRouter(tags=["circulation"])


def _filter_enum(status: Optional[str]) -> int:
    """Translate REST status query into service filter enum."""
    s = (status or "active").lower().strip()
    if s == "returned":
        return 2
    if s == "all":
        return 3
    if s == "overdue":
        return 4
    return 1


@router.post("/borrow", response_model=BorrowRecordRead, status_code=201)
def borrow(
    body: BorrowRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> BorrowRecordRead:
    """Create a borrow record and decrement book availability."""
    now = datetime.now(timezone.utc)
    row = loans_service.borrow_book(
        db,
        settings,
        member_id=str(body.member_id),
        book_id=str(body.book_id),
        due_at_explicit=body.due_date,
        loan_period_days=body.loan_period_days,
    )
    return BorrowRecordRead.from_loan(row, reference_time=now)


@router.post("/return", response_model=BorrowRecordRead)
def return_book(
    body: ReturnRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> BorrowRecordRead:
    """Return an active loan and apply late-fine rules."""
    now = datetime.now(timezone.utc)
    row, _fine = loans_service.return_book(
        db,
        settings,
        loan_id=str(body.loan_id) if body.loan_id else "",
        member_id=str(body.member_id) if body.member_id else "",
        book_id=str(body.book_id) if body.book_id else "",
    )
    return BorrowRecordRead.from_loan(row, reference_time=now)


@router.get("/borrow-records", response_model=PaginatedBorrowRecords)
def list_borrow_records(
    db: Session = Depends(get_db),
    member_id: Optional[str] = Query(default=None),
    book_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default="active", description="active|returned|all|overdue"),
    page_size: int = Query(default=50, ge=1, le=200),
    page_token: str = Query(default=""),
) -> PaginatedBorrowRecords:
    """List borrow history with optional member/book/status filters."""
    now = datetime.now(timezone.utc)
    rows, tok = loans_service.list_loans(
        db,
        member_id=member_id or "",
        book_id=book_id or "",
        filter_enum=_filter_enum(status),
        page_size=page_size,
        page_token=page_token,
    )
    return PaginatedBorrowRecords(
        items=[BorrowRecordRead.from_loan(r, reference_time=now) for r in rows],
        next_page_token=tok,
    )
