"""Process entry: structured logging, DB, gRPC + HTTP servers."""

from __future__ import annotations

import logging
import signal
import sys
import threading
from concurrent import futures

import app  # noqa: F401 — registers generated proto path

from typing import Optional

import grpc
import structlog
import uvicorn
from library.v1 import library_pb2_grpc as pb_grpc

from app.api.app_factory import create_app
from app.api.grpc_servicer import LibraryServicer
from app.core.config import Settings
from app.core.logging_config import configure_logging
from app.db.session import init_engine, ping_database

logger = structlog.get_logger(__name__)


def main() -> None:
    """Initialize dependencies and run gRPC + HTTP servers."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    configure_logging(json_logs=False)
    settings = Settings()
    init_engine(settings)
    try:
        ping_database()
    except Exception as exc:
        logging.getLogger(__name__).exception("database ping failed: %s", exc)
        sys.exit(1)

    app = create_app()

    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_LibraryServiceServicer_to_server(LibraryServicer(settings), grpc_server)
    listen_addr = f"{settings.grpc_host}:{settings.grpc_port}"
    grpc_server.add_insecure_port(listen_addr)
    grpc_server.start()
    logger.info("grpc_listening", addr=listen_addr)

    http_thread = threading.Thread(
        target=lambda: uvicorn.run(
            app,
            host=settings.http_host,
            port=settings.http_port,
            log_level="info",
        ),
        name="uvicorn",
        daemon=True,
    )
    http_thread.start()
    logger.info("http_listening", host=settings.http_host, port=settings.http_port)

    def _stop(_signum: int, _frame: Optional[object]) -> None:
        """Handle process shutdown signals gracefully."""
        logger.info("shutdown_requested")
        grpc_server.stop(grace=5)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    grpc_server.wait_for_termination()


if __name__ == "__main__":
    main()
