"""Pydantic models for REST API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    publication_year: Optional[int] = None
    total_copies: int = Field(default=1, ge=1)


class BookUpdate(BaseModel):
    title: str
    author: str
    isbn: str
    publication_year: Optional[int] = None
    total_copies: Optional[int] = Field(default=None, ge=1)


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    author: str
    isbn: str
    publication_year: Optional[int]
    total_copies: int
    available_copies: int
    created_at: datetime
    updated_at: datetime


class MemberCreate(BaseModel):
    name: str
    email: str
    phone: str
    address: Optional[str] = None


class MemberUpdate(BaseModel):
    name: str
    email: str
    phone: str
    address: Optional[str] = None


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    phone: str
    address: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_member(cls, m: Any) -> MemberRead:
        return cls(
            id=m.id,
            name=m.full_name,
            email=m.email,
            phone=m.phone,
            address=m.address,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class BorrowRequest(BaseModel):
    member_id: UUID
    book_id: UUID
    due_date: Optional[datetime] = None
    loan_period_days: Optional[int] = Field(default=None, ge=1, le=3650)


class ReturnRequest(BaseModel):
    loan_id: Optional[UUID] = None
    member_id: Optional[UUID] = None
    book_id: Optional[UUID] = None


class BorrowRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    member_id: UUID
    book_id: UUID
    borrowed_at: datetime
    due_date: Optional[datetime]
    returned_at: Optional[datetime]
    status: str

    @classmethod
    def from_loan(cls, loan: Any, *, reference_time: datetime) -> BorrowRecordRead:
        from app.services import loans_service

        st = loans_service.loan_display_status(loan, reference_time)
        return cls(
            id=loan.id,
            member_id=loan.member_id,
            book_id=loan.book_id,
            borrowed_at=loan.borrowed_at,
            due_date=loan.due_at,
            returned_at=loan.returned_at,
            status=st,
        )


class PaginatedBooks(BaseModel):
    items: List[BookRead]
    next_page_token: str


class PaginatedMembers(BaseModel):
    items: List[MemberRead]
    next_page_token: str


class PaginatedBorrowRecords(BaseModel):
    items: List[BorrowRecordRead]
    next_page_token: str


class FineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    loan_id: UUID
    member_id: UUID
    amount_cents: int
    currency: str
    status: str
    reason: str
    created_at: datetime
    resolved_at: Optional[datetime]
    notes: Optional[str]


class FineActionRequest(BaseModel):
    notes: Optional[str] = None


class PaginatedFines(BaseModel):
    items: List[FineRead]
    next_page_token: str
