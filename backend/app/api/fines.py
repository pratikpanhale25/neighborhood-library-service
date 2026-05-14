"""Fines REST routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.library import FineActionRequest, FineRead, PaginatedFines
from app.services import fines_service
from app.services.proto_enum_maps import fine_status_filter_from_rest_status

router = APIRouter(prefix="/fines", tags=["fines"])


@router.get("", response_model=PaginatedFines)
def list_fines(
    db: Session = Depends(get_db),
    member_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default="any", description="pending|paid|waived|any"),
    page_size: int = Query(default=50, ge=1, le=200),
    page_token: str = Query(default=""),
) -> PaginatedFines:
    """List fines with member/status filters and pagination."""
    rows, tok = fines_service.list_fines(
        db,
        member_id=member_id or "",
        status_filter_enum=fine_status_filter_from_rest_status(status),
        page_size=page_size,
        page_token=page_token,
    )
    return PaginatedFines(items=[FineRead.model_validate(r) for r in rows], next_page_token=tok)


@router.get("/{fine_id}", response_model=FineRead)
def get_fine(fine_id: str, db: Session = Depends(get_db)) -> FineRead:
    """Fetch a single fine by id."""
    row = fines_service.get_fine(db, fine_id=fine_id)
    return FineRead.model_validate(row)


@router.post("/{fine_id}/pay", response_model=FineRead)
def pay_fine(
    fine_id: str,
    body: FineActionRequest,
    db: Session = Depends(get_db),
) -> FineRead:
    """Mark a pending fine as paid."""
    row = fines_service.pay_fine(db, fine_id=fine_id, notes=body.notes or "")
    return FineRead.model_validate(row)


@router.post("/{fine_id}/waive", response_model=FineRead)
def waive_fine(
    fine_id: str,
    body: FineActionRequest,
    db: Session = Depends(get_db),
) -> FineRead:
    """Mark a pending fine as waived."""
    row = fines_service.waive_fine(db, fine_id=fine_id, notes=body.notes or "")
    return FineRead.model_validate(row)
