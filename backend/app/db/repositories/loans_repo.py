"""Loan row reads/locks (ORM only).

Concurrency: ``with_for_update`` calls stay here so return/borrow paths stay obvious.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.entities import Book, Loan, Member


def fetch_member(session: Session, member_id: uuid.UUID) -> Optional[Member]:
    return session.get(Member, member_id)


def fetch_book_for_update(session: Session, book_id: uuid.UUID) -> Optional[Book]:
    return session.execute(select(Book).where(Book.id == book_id).with_for_update()).scalar_one_or_none()


def find_active_loan(session: Session, member_id: uuid.UUID, book_id: uuid.UUID) -> Optional[Loan]:
    return session.scalar(
        select(Loan).where(
            and_(
                Loan.member_id == member_id,
                Loan.book_id == book_id,
                Loan.returned_at.is_(None),
            )
        )
    )


def fetch_loan_by_id_for_update(session: Session, loan_id: uuid.UUID) -> Optional[Loan]:
    return session.execute(
        select(Loan).where(Loan.id == loan_id).with_for_update()
    ).scalar_one_or_none()


def fetch_active_loan_member_book_for_update(
    session: Session, member_id: uuid.UUID, book_id: uuid.UUID
) -> Optional[Loan]:
    return session.scalar(
        select(Loan)
        .where(
            and_(
                Loan.member_id == member_id,
                Loan.book_id == book_id,
                Loan.returned_at.is_(None),
            )
        )
        .with_for_update()
    )


def fetch_book_for_update_by_id(session: Session, book_id: uuid.UUID) -> Book:
    return session.execute(select(Book).where(Book.id == book_id).with_for_update()).scalar_one()


def list_loans_page(
    session: Session,
    *,
    where_conds: list,
    offset: int,
    limit_plus_one: int,
) -> List[Loan]:
    q = select(Loan)
    if where_conds:
        q = q.where(and_(*where_conds))
    q = q.order_by(Loan.borrowed_at.desc(), Loan.id.desc()).offset(offset).limit(limit_plus_one)
    return list(session.scalars(q).all())


def list_active_loans_for_member(session: Session, member_id: uuid.UUID) -> List[Loan]:
    q = (
        select(Loan)
        .where(and_(Loan.member_id == member_id, Loan.returned_at.is_(None)))
        .order_by(Loan.borrowed_at.desc())
    )
    return list(session.scalars(q).all())
