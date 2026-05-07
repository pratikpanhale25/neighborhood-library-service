"""gRPC ``LibraryService`` implementation (thin adapter over services)."""

from __future__ import annotations

from datetime import datetime, timezone

import grpc
from library.v1 import library_pb2 as pb
from library.v1 import library_pb2_grpc as pb_grpc
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db import session as db_session
from app.services import books_service, fines_service, loans_service, members_service
from app.services.exceptions import (
    BookAlreadyOnLoanError,
    BookNotFoundError,
    DomainError,
    FineNotFoundError,
    InvalidFineStateError,
    InvalidReturnError,
    LoanNotFoundError,
    MemberNotFoundError,
    NoCopiesAvailableError,
    NotFoundError,
    ValidationError,
)
from app.utils import timeutil


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _book_to_pb(b: object) -> pb.Book:
    msg = pb.Book()
    msg.id = str(b.id)
    msg.title = b.title
    msg.author = b.author
    msg.isbn = b.isbn or ""
    msg.publication_year = b.publication_year if b.publication_year is not None else 0
    msg.total_copies = int(b.total_copies)
    msg.available_copies = int(b.available_copies)
    ca = timeutil.datetime_to_pb(b.created_at)
    if ca is not None:
        msg.created_at.CopyFrom(ca)
    ua = timeutil.datetime_to_pb(b.updated_at)
    if ua is not None:
        msg.updated_at.CopyFrom(ua)
    return msg


def _member_to_pb(m: object) -> pb.Member:
    msg = pb.Member()
    msg.id = str(m.id)
    msg.full_name = m.full_name
    msg.email = m.email
    msg.phone = m.phone
    msg.address = m.address or ""
    ca = timeutil.datetime_to_pb(m.created_at)
    if ca is not None:
        msg.created_at.CopyFrom(ca)
    ua = timeutil.datetime_to_pb(m.updated_at)
    if ua is not None:
        msg.updated_at.CopyFrom(ua)
    return msg


def _loan_to_pb(loan: object, *, reference_time: datetime) -> pb.Loan:
    msg = pb.Loan()
    msg.id = str(loan.id)
    msg.book_id = str(loan.book_id)
    msg.member_id = str(loan.member_id)
    ba = timeutil.datetime_to_pb(loan.borrowed_at)
    if ba is not None:
        msg.borrowed_at.CopyFrom(ba)
    da = timeutil.datetime_to_pb(loan.due_at)
    if da is not None:
        msg.due_at.CopyFrom(da)
    ra = timeutil.datetime_to_pb(loan.returned_at)
    if ra is not None:
        msg.returned_at.CopyFrom(ra)
    is_od, days_od = loans_service.loan_overdue_flags(loan, reference_time)
    msg.is_overdue = is_od
    msg.days_overdue = days_od
    msg.status = loans_service.loan_display_status(loan, reference_time)
    return msg


def _fine_to_pb(f: object) -> pb.Fine:
    msg = pb.Fine()
    msg.id = str(f.id)
    msg.loan_id = str(f.loan_id)
    msg.member_id = str(f.member_id)
    msg.amount_cents = f.amount_cents
    msg.currency = f.currency
    msg.status = f.status
    msg.reason = f.reason
    ca = timeutil.datetime_to_pb(f.created_at)
    if ca is not None:
        msg.created_at.CopyFrom(ca)
    ra = timeutil.datetime_to_pb(f.resolved_at)
    if ra is not None:
        msg.resolved_at.CopyFrom(ra)
    msg.notes = f.notes or ""
    return msg


def _abort_domain(context: grpc.ServicerContext, exc: BaseException) -> None:
    if isinstance(exc, ValidationError):
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))
    elif isinstance(exc, (BookNotFoundError, MemberNotFoundError, LoanNotFoundError, FineNotFoundError)):
        context.abort(grpc.StatusCode.NOT_FOUND, str(exc))
    elif isinstance(
        exc,
        (
            BookAlreadyOnLoanError,
            NoCopiesAvailableError,
            InvalidReturnError,
            InvalidFineStateError,
        ),
    ):
        context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(exc))
    elif isinstance(exc, NotFoundError):
        context.abort(grpc.StatusCode.NOT_FOUND, str(exc))
    elif isinstance(exc, DomainError):
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))
    else:
        context.abort(grpc.StatusCode.INTERNAL, "internal error")


class LibraryServicer(pb_grpc.LibraryServiceServicer):
    """Routes each RPC to the service layer using a per-request DB session."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _session(self) -> Session:
        if db_session.SessionLocal is None:
            raise RuntimeError("database not initialized")
        return db_session.SessionLocal()

    def CreateBook(
        self,
        request: pb.CreateBookRequest,
        context: grpc.ServicerContext,
    ) -> pb.CreateBookResponse:
        try:
            db = self._session()
            try:
                total = (
                    request.total_copies
                    if request.HasField("total_copies") and request.total_copies > 0
                    else 1
                )
                row = books_service.create_book(
                    db,
                    title=request.title,
                    author=request.author,
                    isbn=request.isbn,
                    publication_year=request.publication_year or None,
                    total_copies=total,
                )
                db.commit()
                return pb.CreateBookResponse(book=_book_to_pb(row))
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
        except (ValidationError, DomainError) as exc:
            _abort_domain(context, exc)

    def UpdateBook(
        self,
        request: pb.UpdateBookRequest,
        context: grpc.ServicerContext,
    ) -> pb.UpdateBookResponse:
        try:
            db = self._session()
            try:
                tc = request.total_copies if request.HasField("total_copies") else None
                if tc is not None and tc < 1:
                    tc = 1
                row = books_service.update_book(
                    db,
                    book_id=request.id,
                    title=request.title,
                    author=request.author,
                    isbn=request.isbn,
                    publication_year=request.publication_year or None,
                    total_copies=tc,
                )
                db.commit()
                return pb.UpdateBookResponse(book=_book_to_pb(row))
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
        except (ValidationError, BookNotFoundError, DomainError) as exc:
            _abort_domain(context, exc)

    def GetBook(
        self,
        request: pb.GetBookRequest,
        context: grpc.ServicerContext,
    ) -> pb.GetBookResponse:
        try:
            db = self._session()
            try:
                row = books_service.get_book(db, book_id=request.id)
                return pb.GetBookResponse(book=_book_to_pb(row))
            finally:
                db.close()
        except (ValidationError, BookNotFoundError, DomainError) as exc:
            _abort_domain(context, exc)

    def ListBooks(
        self,
        request: pb.ListBooksRequest,
        context: grpc.ServicerContext,
    ) -> pb.ListBooksResponse:
        try:
            db = self._session()
            try:
                rows, next_tok = books_service.list_books(
                    db,
                    page_size=request.page_size,
                    page_token=request.page_token,
                )
                return pb.ListBooksResponse(
                    books=[_book_to_pb(r) for r in rows],
                    next_page_token=next_tok,
                )
            finally:
                db.close()
        except (ValidationError, DomainError) as exc:
            _abort_domain(context, exc)

    def CreateMember(
        self,
        request: pb.CreateMemberRequest,
        context: grpc.ServicerContext,
    ) -> pb.CreateMemberResponse:
        try:
            db = self._session()
            try:
                row = members_service.create_member(
                    db,
                    full_name=request.full_name,
                    email=request.email,
                    phone=request.phone,
                    address=request.address,
                )
                db.commit()
                return pb.CreateMemberResponse(member=_member_to_pb(row))
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
        except (ValidationError, DomainError) as exc:
            _abort_domain(context, exc)

    def UpdateMember(
        self,
        request: pb.UpdateMemberRequest,
        context: grpc.ServicerContext,
    ) -> pb.UpdateMemberResponse:
        try:
            db = self._session()
            try:
                row = members_service.update_member(
                    db,
                    member_id=request.id,
                    full_name=request.full_name,
                    email=request.email,
                    phone=request.phone,
                    address=request.address,
                )
                db.commit()
                return pb.UpdateMemberResponse(member=_member_to_pb(row))
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
        except (ValidationError, DomainError) as exc:
            _abort_domain(context, exc)

    def GetMember(
        self,
        request: pb.GetMemberRequest,
        context: grpc.ServicerContext,
    ) -> pb.GetMemberResponse:
        try:
            db = self._session()
            try:
                row = members_service.get_member(db, member_id=request.id)
                return pb.GetMemberResponse(member=_member_to_pb(row))
            finally:
                db.close()
        except (ValidationError, DomainError) as exc:
            _abort_domain(context, exc)

    def ListMembers(
        self,
        request: pb.ListMembersRequest,
        context: grpc.ServicerContext,
    ) -> pb.ListMembersResponse:
        try:
            db = self._session()
            try:
                rows, next_tok = members_service.list_members(
                    db,
                    page_size=request.page_size,
                    page_token=request.page_token,
                )
                return pb.ListMembersResponse(
                    members=[_member_to_pb(r) for r in rows],
                    next_page_token=next_tok,
                )
            finally:
                db.close()
        except (ValidationError, DomainError) as exc:
            _abort_domain(context, exc)

    def BorrowBook(
        self,
        request: pb.BorrowBookRequest,
        context: grpc.ServicerContext,
    ) -> pb.BorrowBookResponse:
        try:
            db = self._session()
            try:
                due = timeutil.pb_to_datetime(request.due_at)
                period = (
                    request.loan_period_days
                    if request.HasField("loan_period_days")
                    else None
                )
                row = loans_service.borrow_book(
                    db,
                    self._settings,
                    member_id=request.member_id,
                    book_id=request.book_id,
                    due_at_explicit=due,
                    loan_period_days=period,
                )
                db.commit()
                now = _utc_now()
                return pb.BorrowBookResponse(loan=_loan_to_pb(row, reference_time=now))
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
        except (
            ValidationError,
            BookNotFoundError,
            MemberNotFoundError,
            BookAlreadyOnLoanError,
            NoCopiesAvailableError,
            DomainError,
        ) as exc:
            _abort_domain(context, exc)

    def ReturnBook(
        self,
        request: pb.ReturnBookRequest,
        context: grpc.ServicerContext,
    ) -> pb.ReturnBookResponse:
        try:
            db = self._session()
            try:
                row, created_fine = loans_service.return_book(
                    db,
                    self._settings,
                    loan_id=request.loan_id,
                    member_id=request.member_id,
                    book_id=request.book_id,
                )
                db.commit()
                now = _utc_now()
                resp = pb.ReturnBookResponse(loan=_loan_to_pb(row, reference_time=now))
                if created_fine is not None:
                    resp.created_fine.CopyFrom(_fine_to_pb(created_fine))
                return resp
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
        except (
            ValidationError,
            LoanNotFoundError,
            InvalidReturnError,
            DomainError,
        ) as exc:
            _abort_domain(context, exc)

    def ListLoans(
        self,
        request: pb.ListLoansRequest,
        context: grpc.ServicerContext,
    ) -> pb.ListLoansResponse:
        try:
            db = self._session()
            try:
                rows, next_tok = loans_service.list_loans(
                    db,
                    member_id=request.member_id,
                    book_id=request.book_id,
                    filter_enum=request.filter,
                    page_size=request.page_size,
                    page_token=request.page_token,
                )
                now = _utc_now()
                return pb.ListLoansResponse(
                    loans=[_loan_to_pb(r, reference_time=now) for r in rows],
                    next_page_token=next_tok,
                )
            finally:
                db.close()
        except (ValidationError, DomainError) as exc:
            _abort_domain(context, exc)

    def ListFines(
        self,
        request: pb.ListFinesRequest,
        context: grpc.ServicerContext,
    ) -> pb.ListFinesResponse:
        try:
            db = self._session()
            try:
                rows, next_tok = fines_service.list_fines(
                    db,
                    member_id=request.member_id,
                    status_filter_enum=request.status_filter,
                    page_size=request.page_size,
                    page_token=request.page_token,
                )
                return pb.ListFinesResponse(
                    fines=[_fine_to_pb(r) for r in rows],
                    next_page_token=next_tok,
                )
            finally:
                db.close()
        except (ValidationError, DomainError) as exc:
            _abort_domain(context, exc)

    def GetFine(
        self,
        request: pb.GetFineRequest,
        context: grpc.ServicerContext,
    ) -> pb.GetFineResponse:
        try:
            db = self._session()
            try:
                row = fines_service.get_fine(db, fine_id=request.id)
                return pb.GetFineResponse(fine=_fine_to_pb(row))
            finally:
                db.close()
        except (ValidationError, FineNotFoundError, DomainError) as exc:
            _abort_domain(context, exc)

    def PayFine(
        self,
        request: pb.PayFineRequest,
        context: grpc.ServicerContext,
    ) -> pb.PayFineResponse:
        try:
            db = self._session()
            try:
                row = fines_service.pay_fine(db, fine_id=request.fine_id, notes=request.notes)
                db.commit()
                return pb.PayFineResponse(fine=_fine_to_pb(row))
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
        except (ValidationError, FineNotFoundError, InvalidFineStateError, DomainError) as exc:
            _abort_domain(context, exc)

    def WaiveFine(
        self,
        request: pb.WaiveFineRequest,
        context: grpc.ServicerContext,
    ) -> pb.WaiveFineResponse:
        try:
            db = self._session()
            try:
                row = fines_service.waive_fine(db, fine_id=request.fine_id, notes=request.notes)
                db.commit()
                return pb.WaiveFineResponse(fine=_fine_to_pb(row))
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()
        except (ValidationError, FineNotFoundError, InvalidFineStateError, DomainError) as exc:
            _abort_domain(context, exc)
