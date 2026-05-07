"""FastAPI dependencies."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db import session as db_session


def get_settings() -> Settings:
    """Provide request-scoped settings object."""
    return Settings()


def get_db() -> Generator[Session, None, None]:
    """Provide transactional DB session per request."""
    if db_session.SessionLocal is None:
        raise RuntimeError("Database not initialized")
    db = db_session.SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
