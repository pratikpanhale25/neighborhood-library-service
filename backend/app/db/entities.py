"""SQLAlchemy ORM entities."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    pass


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint("total_copies >= 1", name="books_total_copies_min"),
        CheckConstraint("available_copies >= 0", name="books_available_non_negative"),
        CheckConstraint("available_copies <= total_copies", name="books_available_lte_total"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False)
    isbn: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    publication_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_copies: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    available_copies: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    loans: Mapped[list[Loan]] = relationship(back_populates="book")


class Member(Base):
    __tablename__ = "members"
    __table_args__ = ()

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    loans: Mapped[list[Loan]] = relationship(back_populates="member")


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (
        Index(
            "uq_loans_active_member_book",
            "member_id",
            "book_id",
            unique=True,
            postgresql_where=text("returned_at IS NULL"),
        ),
        Index("ix_loans_book_id", "book_id"),
        Index("ix_loans_member_returned", "member_id", "returned_at"),
        CheckConstraint(
            "status IN ('BORROWED','RETURNED')",
            name="loans_status_chk",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="RESTRICT"), nullable=False
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=False
    )
    borrowed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="BORROWED")

    book: Mapped[Book] = relationship(back_populates="loans")
    member: Mapped[Member] = relationship(back_populates="loans")
    fines: Mapped[list[Fine]] = relationship(back_populates="loan")


class Fine(Base):
    __tablename__ = "fines"
    __table_args__ = (
        Index(
            "uq_fines_one_pending_per_loan",
            "loan_id",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
        Index("ix_fines_member_status", "member_id", "status"),
        CheckConstraint("amount_cents >= 0", name="fines_amount_non_negative"),
        CheckConstraint("status IN ('pending','paid','waived')", name="fines_status_chk"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    loan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("loans.id", ondelete="RESTRICT"), nullable=False
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=False
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="USD")
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False, server_default="overdue")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    loan: Mapped[Loan] = relationship(back_populates="fines")
