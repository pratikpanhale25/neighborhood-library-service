"""FastAPI application factory."""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import books, circulation, fines, health, members
from app.api.errors import register_exception_handlers


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    app = FastAPI(
        title="Neighborhood Library",
        version="0.2.0",
        description="REST API for books, members, and circulation (gRPC also available).",
    )
    register_exception_handlers(app)

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Attach a request id header for traceability."""
        rid = str(uuid.uuid4())
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(books.router)
    app.include_router(members.router)
    app.include_router(circulation.router)
    app.include_router(fines.router)
    return app
