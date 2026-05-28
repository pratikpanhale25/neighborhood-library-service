"""Borrow / return / borrow-records REST routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_settings
from app.core.config import Settings
from app.schemas.library import BorrowRecordRead, BorrowRequest, PaginatedBorrowRecords, ReturnRequest
from app.services import loans_service
from app.services.proto_enum_maps import loan_filter_from_rest_status
from app.utils import timeutil

router = APIRouter(tags=["circulation"])


@router.post("/borrow", response_model=BorrowRecordRead, status_code=201)
def borrow(
    body: BorrowRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> BorrowRecordRead:
    """Create a borrow record and decrement book availability."""
    now = timeutil.utc_now()
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
    now = timeutil.utc_now()
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
    now = timeutil.utc_now()
    rows, tok = loans_service.list_loans(
        db,
        member_id=member_id or "",
        book_id=book_id or "",
        filter_enum=loan_filter_from_rest_status(status),
        page_size=page_size,
        page_token=page_token,
    )
    return PaginatedBorrowRecords(
        items=[BorrowRecordRead.from_loan(r, reference_time=now) for r in rows],
        next_page_token=tok,
    )
