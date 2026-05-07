"""Input validation helpers."""

from __future__ import annotations

import uuid

from app.services.exceptions import ValidationError


def ensure_uuid(field: str, value: str) -> uuid.UUID:
    """Parse ``value`` as UUID or raise ValidationError."""
    try:
        return uuid.UUID(str(value).strip())
    except (ValueError, AttributeError) as exc:
        raise ValidationError(f"invalid {field}", code="validation") from exc
