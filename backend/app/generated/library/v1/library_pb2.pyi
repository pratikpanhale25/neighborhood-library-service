import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LoanFilter(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOAN_FILTER_UNSPECIFIED: _ClassVar[LoanFilter]
    LOAN_FILTER_ACTIVE_ONLY: _ClassVar[LoanFilter]
    LOAN_FILTER_RETURNED_ONLY: _ClassVar[LoanFilter]
    LOAN_FILTER_ALL: _ClassVar[LoanFilter]
    LOAN_FILTER_OVERDUE_ONLY: _ClassVar[LoanFilter]

class FineStatusFilter(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FINE_STATUS_FILTER_UNSPECIFIED: _ClassVar[FineStatusFilter]
    FINE_STATUS_FILTER_PENDING: _ClassVar[FineStatusFilter]
    FINE_STATUS_FILTER_PAID: _ClassVar[FineStatusFilter]
    FINE_STATUS_FILTER_WAIVED: _ClassVar[FineStatusFilter]
    FINE_STATUS_FILTER_ANY: _ClassVar[FineStatusFilter]
LOAN_FILTER_UNSPECIFIED: LoanFilter
LOAN_FILTER_ACTIVE_ONLY: LoanFilter
LOAN_FILTER_RETURNED_ONLY: LoanFilter
LOAN_FILTER_ALL: LoanFilter
LOAN_FILTER_OVERDUE_ONLY: LoanFilter
FINE_STATUS_FILTER_UNSPECIFIED: FineStatusFilter
FINE_STATUS_FILTER_PENDING: FineStatusFilter
FINE_STATUS_FILTER_PAID: FineStatusFilter
FINE_STATUS_FILTER_WAIVED: FineStatusFilter
FINE_STATUS_FILTER_ANY: FineStatusFilter

class Book(_message.Message):
    __slots__ = ("id", "title", "author", "isbn", "publication_year", "created_at", "updated_at", "total_copies", "available_copies")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    ISBN_FIELD_NUMBER: _ClassVar[int]
    PUBLICATION_YEAR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COPIES_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_COPIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    author: str
    isbn: str
    publication_year: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    total_copies: int
    available_copies: int
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ..., isbn: _Optional[str] = ..., publication_year: _Optional[int] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., total_copies: _Optional[int] = ..., available_copies: _Optional[int] = ...) -> None: ...

class Member(_message.Message):
    __slots__ = ("id", "full_name", "email", "phone", "address", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    full_name: str
    email: str
    phone: str
    address: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., full_name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., address: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Loan(_message.Message):
    __slots__ = ("id", "book_id", "member_id", "borrowed_at", "due_at", "returned_at", "is_overdue", "days_overdue", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    BORROWED_AT_FIELD_NUMBER: _ClassVar[int]
    DUE_AT_FIELD_NUMBER: _ClassVar[int]
    RETURNED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_OVERDUE_FIELD_NUMBER: _ClassVar[int]
    DAYS_OVERDUE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    book_id: str
    member_id: str
    borrowed_at: _timestamp_pb2.Timestamp
    due_at: _timestamp_pb2.Timestamp
    returned_at: _timestamp_pb2.Timestamp
    is_overdue: bool
    days_overdue: int
    status: str
    def __init__(self, id: _Optional[str] = ..., book_id: _Optional[str] = ..., member_id: _Optional[str] = ..., borrowed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., due_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., returned_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., is_overdue: bool = ..., days_overdue: _Optional[int] = ..., status: _Optional[str] = ...) -> None: ...

class Fine(_message.Message):
    __slots__ = ("id", "loan_id", "member_id", "amount_cents", "currency", "status", "reason", "created_at", "resolved_at", "notes")
    ID_FIELD_NUMBER: _ClassVar[int]
    LOAN_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_CENTS_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_AT_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    id: str
    loan_id: str
    member_id: str
    amount_cents: int
    currency: str
    status: str
    reason: str
    created_at: _timestamp_pb2.Timestamp
    resolved_at: _timestamp_pb2.Timestamp
    notes: str
    def __init__(self, id: _Optional[str] = ..., loan_id: _Optional[str] = ..., member_id: _Optional[str] = ..., amount_cents: _Optional[int] = ..., currency: _Optional[str] = ..., status: _Optional[str] = ..., reason: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., resolved_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., notes: _Optional[str] = ...) -> None: ...

class CreateBookRequest(_message.Message):
    __slots__ = ("title", "author", "isbn", "publication_year", "total_copies")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    ISBN_FIELD_NUMBER: _ClassVar[int]
    PUBLICATION_YEAR_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COPIES_FIELD_NUMBER: _ClassVar[int]
    title: str
    author: str
    isbn: str
    publication_year: int
    total_copies: int
    def __init__(self, title: _Optional[str] = ..., author: _Optional[str] = ..., isbn: _Optional[str] = ..., publication_year: _Optional[int] = ..., total_copies: _Optional[int] = ...) -> None: ...

class CreateBookResponse(_message.Message):
    __slots__ = ("book",)
    BOOK_FIELD_NUMBER: _ClassVar[int]
    book: Book
    def __init__(self, book: _Optional[_Union[Book, _Mapping]] = ...) -> None: ...

class UpdateBookRequest(_message.Message):
    __slots__ = ("id", "title", "author", "isbn", "publication_year", "total_copies")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    ISBN_FIELD_NUMBER: _ClassVar[int]
    PUBLICATION_YEAR_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COPIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    author: str
    isbn: str
    publication_year: int
    total_copies: int
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ..., isbn: _Optional[str] = ..., publication_year: _Optional[int] = ..., total_copies: _Optional[int] = ...) -> None: ...

class UpdateBookResponse(_message.Message):
    __slots__ = ("book",)
    BOOK_FIELD_NUMBER: _ClassVar[int]
    book: Book
    def __init__(self, book: _Optional[_Union[Book, _Mapping]] = ...) -> None: ...

class GetBookRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetBookResponse(_message.Message):
    __slots__ = ("book",)
    BOOK_FIELD_NUMBER: _ClassVar[int]
    book: Book
    def __init__(self, book: _Optional[_Union[Book, _Mapping]] = ...) -> None: ...

class ListBooksRequest(_message.Message):
    __slots__ = ("page_size", "page_token")
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListBooksResponse(_message.Message):
    __slots__ = ("books", "next_page_token")
    BOOKS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    books: _containers.RepeatedCompositeFieldContainer[Book]
    next_page_token: str
    def __init__(self, books: _Optional[_Iterable[_Union[Book, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class CreateMemberRequest(_message.Message):
    __slots__ = ("full_name", "email", "phone", "address")
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    full_name: str
    email: str
    phone: str
    address: str
    def __init__(self, full_name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class CreateMemberResponse(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: Member
    def __init__(self, member: _Optional[_Union[Member, _Mapping]] = ...) -> None: ...

class UpdateMemberRequest(_message.Message):
    __slots__ = ("id", "full_name", "email", "phone", "address")
    ID_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    id: str
    full_name: str
    email: str
    phone: str
    address: str
    def __init__(self, id: _Optional[str] = ..., full_name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class UpdateMemberResponse(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: Member
    def __init__(self, member: _Optional[_Union[Member, _Mapping]] = ...) -> None: ...

class GetMemberRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetMemberResponse(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: Member
    def __init__(self, member: _Optional[_Union[Member, _Mapping]] = ...) -> None: ...

class ListMembersRequest(_message.Message):
    __slots__ = ("page_size", "page_token")
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListMembersResponse(_message.Message):
    __slots__ = ("members", "next_page_token")
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    members: _containers.RepeatedCompositeFieldContainer[Member]
    next_page_token: str
    def __init__(self, members: _Optional[_Iterable[_Union[Member, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class BorrowBookRequest(_message.Message):
    __slots__ = ("member_id", "book_id", "due_at", "loan_period_days")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    DUE_AT_FIELD_NUMBER: _ClassVar[int]
    LOAN_PERIOD_DAYS_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    book_id: str
    due_at: _timestamp_pb2.Timestamp
    loan_period_days: int
    def __init__(self, member_id: _Optional[str] = ..., book_id: _Optional[str] = ..., due_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., loan_period_days: _Optional[int] = ...) -> None: ...

class BorrowBookResponse(_message.Message):
    __slots__ = ("loan",)
    LOAN_FIELD_NUMBER: _ClassVar[int]
    loan: Loan
    def __init__(self, loan: _Optional[_Union[Loan, _Mapping]] = ...) -> None: ...

class ReturnBookRequest(_message.Message):
    __slots__ = ("loan_id", "member_id", "book_id")
    LOAN_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    loan_id: str
    member_id: str
    book_id: str
    def __init__(self, loan_id: _Optional[str] = ..., member_id: _Optional[str] = ..., book_id: _Optional[str] = ...) -> None: ...

class ReturnBookResponse(_message.Message):
    __slots__ = ("loan", "created_fine")
    LOAN_FIELD_NUMBER: _ClassVar[int]
    CREATED_FINE_FIELD_NUMBER: _ClassVar[int]
    loan: Loan
    created_fine: Fine
    def __init__(self, loan: _Optional[_Union[Loan, _Mapping]] = ..., created_fine: _Optional[_Union[Fine, _Mapping]] = ...) -> None: ...

class ListLoansRequest(_message.Message):
    __slots__ = ("member_id", "book_id", "filter", "page_size", "page_token")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    book_id: str
    filter: LoanFilter
    page_size: int
    page_token: str
    def __init__(self, member_id: _Optional[str] = ..., book_id: _Optional[str] = ..., filter: _Optional[_Union[LoanFilter, str]] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListLoansResponse(_message.Message):
    __slots__ = ("loans", "next_page_token")
    LOANS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    loans: _containers.RepeatedCompositeFieldContainer[Loan]
    next_page_token: str
    def __init__(self, loans: _Optional[_Iterable[_Union[Loan, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class ListFinesRequest(_message.Message):
    __slots__ = ("member_id", "status_filter", "page_size", "page_token")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FILTER_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    member_id: str
    status_filter: FineStatusFilter
    page_size: int
    page_token: str
    def __init__(self, member_id: _Optional[str] = ..., status_filter: _Optional[_Union[FineStatusFilter, str]] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListFinesResponse(_message.Message):
    __slots__ = ("fines", "next_page_token")
    FINES_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    fines: _containers.RepeatedCompositeFieldContainer[Fine]
    next_page_token: str
    def __init__(self, fines: _Optional[_Iterable[_Union[Fine, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class GetFineRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetFineResponse(_message.Message):
    __slots__ = ("fine",)
    FINE_FIELD_NUMBER: _ClassVar[int]
    fine: Fine
    def __init__(self, fine: _Optional[_Union[Fine, _Mapping]] = ...) -> None: ...

class PayFineRequest(_message.Message):
    __slots__ = ("fine_id", "notes")
    FINE_ID_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    fine_id: str
    notes: str
    def __init__(self, fine_id: _Optional[str] = ..., notes: _Optional[str] = ...) -> None: ...

class PayFineResponse(_message.Message):
    __slots__ = ("fine",)
    FINE_FIELD_NUMBER: _ClassVar[int]
    fine: Fine
    def __init__(self, fine: _Optional[_Union[Fine, _Mapping]] = ...) -> None: ...

class WaiveFineRequest(_message.Message):
    __slots__ = ("fine_id", "notes")
    FINE_ID_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    fine_id: str
    notes: str
    def __init__(self, fine_id: _Optional[str] = ..., notes: _Optional[str] = ...) -> None: ...

class WaiveFineResponse(_message.Message):
    __slots__ = ("fine",)
    FINE_FIELD_NUMBER: _ClassVar[int]
    fine: Fine
    def __init__(self, fine: _Optional[_Union[Fine, _Mapping]] = ...) -> None: ...
