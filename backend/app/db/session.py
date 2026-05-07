"""SQLAlchemy engine and session factory."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from typing import Optional

from sqlalchemy import create_engine, text

from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings

_engine = None
SessionLocal: Optional[sessionmaker[Session]] = None


def init_engine(settings: Settings) -> None:
    """Create global engine and :class:`sessionmaker` (idempotent)."""
    global _engine, SessionLocal
    if _engine is not None:
        return
    _engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        future=True,
    )
    SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_engine():
    """Return the configured SQLAlchemy engine."""
    if _engine is None:
        raise RuntimeError("init_engine was not called")
    return _engine


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    if SessionLocal is None:
        raise RuntimeError("init_engine was not called")
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def ping_database() -> None:
    """Raise if the database is unreachable."""
    eng = get_engine()
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
