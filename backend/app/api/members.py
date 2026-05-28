"""Member REST routes."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.library import (
    BorrowRecordRead,
    MemberCreate,
    MemberRead,
    MemberUpdate,
    PaginatedMembers,
)
from app.services import loans_service, members_service
from app.utils import timeutil

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=MemberRead, status_code=201)
def create_member(body: MemberCreate, db: Session = Depends(get_db)) -> MemberRead:
    """Create a new library member."""
    row = members_service.create_member(
        db,
        full_name=body.name,
        email=body.email,
        phone=body.phone,
        address=body.address or "",
    )
    return MemberRead.from_member(row)


@router.get("", response_model=PaginatedMembers)
def list_members(
    db: Session = Depends(get_db),
    page_size: int = Query(default=50, ge=1, le=200),
    page_token: str = Query(default=""),
    query: Optional[str] = Query(default=None, description="Substring match on name or email"),
) -> PaginatedMembers:
    """List members with pagination."""
    rows, tok = members_service.list_members(db, page_size=page_size, page_token=page_token, query=query)
    return PaginatedMembers(
        items=[MemberRead.from_member(r) for r in rows],
        next_page_token=tok,
    )


@router.get("/{member_id}/borrowed-books", response_model=List[BorrowRecordRead])
def borrowed_books(member_id: str, db: Session = Depends(get_db)) -> List[BorrowRecordRead]:
    """Return active borrowed books for a member."""
    now = timeutil.utc_now()
    rows = loans_service.list_active_loans_for_member(db, member_id=member_id)
    return [BorrowRecordRead.from_loan(r, reference_time=now) for r in rows]


@router.get("/{member_id}", response_model=MemberRead)
def get_member(member_id: str, db: Session = Depends(get_db)) -> MemberRead:
    """Fetch one member by id."""
    row = members_service.get_member(db, member_id=member_id)
    return MemberRead.from_member(row)


@router.put("/{member_id}", response_model=MemberRead)
def update_member(member_id: str, body: MemberUpdate, db: Session = Depends(get_db)) -> MemberRead:
    """Update an existing member by id."""
    row = members_service.update_member(
        db,
        member_id=member_id,
        full_name=body.name,
        email=body.email,
        phone=body.phone,
        address=body.address or "",
    )
    return MemberRead.from_member(row)
