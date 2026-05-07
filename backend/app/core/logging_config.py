"""Structured logging setup."""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(json_logs: bool = False) -> None:
    """Configure stdlib logging + structlog for JSON or console output."""
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    shared: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        timestamper,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if json_logs:
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processor=structlog.processors.JSONRenderer(),
        )
    else:
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processor=structlog.dev.ConsoleRenderer(colors=False),
        )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    structlog.configure(
        processors=shared
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
