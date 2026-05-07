"""Domain-level exceptions."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for predictable domain failures."""

    def __init__(self, message: str, *, code: str = "") -> None:
        super().__init__(message)
        self.code = code


class ValidationError(DomainError):
    """Input failed validation rules."""

    pass


class NotFoundError(DomainError):
    """A referenced entity does not exist."""

    pass


class BookNotFoundError(NotFoundError):
    """No book with the given id."""

    pass


class MemberNotFoundError(NotFoundError):
    """No member with the given id."""

    pass


class LoanNotFoundError(NotFoundError):
    """No matching loan (or not in the required state)."""

    pass


class BookAlreadyOnLoanError(DomainError):
    """Legacy name: member already has an active borrow for this book."""

    pass


class NoCopiesAvailableError(DomainError):
    """No copies left to borrow."""

    pass


class InvalidReturnError(DomainError):
    """Return could not be applied."""

    pass


class FineNotFoundError(NotFoundError):
    """No fine with the given id."""

    pass


class InvalidFineStateError(DomainError):
    """Fine cannot be paid or waived in its current state."""

    pass
