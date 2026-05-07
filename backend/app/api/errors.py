"""Map domain errors to HTTP responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.exceptions import (
    BookAlreadyOnLoanError,
    DomainError,
    InvalidFineStateError,
    InvalidReturnError,
    NoCopiesAvailableError,
    NotFoundError,
    ValidationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    async def _validation(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc), "code": getattr(exc, "code", "")},
        )

    @app.exception_handler(NotFoundError)
    async def _not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc), "code": getattr(exc, "code", "")},
        )

    async def _conflict(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc), "code": getattr(exc, "code", "")},
        )

    for _cls in (
        BookAlreadyOnLoanError,
        NoCopiesAvailableError,
        InvalidReturnError,
        InvalidFineStateError,
    ):
        app.add_exception_handler(_cls, _conflict)

    @app.exception_handler(DomainError)
    async def _domain(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "code": getattr(exc, "code", "")},
        )
