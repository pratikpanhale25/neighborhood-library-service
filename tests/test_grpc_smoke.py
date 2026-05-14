"""Minimal gRPC round-trip against LibraryServicer (requires PostgreSQL)."""

from __future__ import annotations

import os
import uuid
from concurrent import futures

import grpc
import pytest
from grpc_reflection.v1alpha import reflection
from library.v1 import library_pb2 as pb
from library.v1 import library_pb2_grpc as pb_grpc

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def grpc_stub():
    """Start in-process gRPC server with reflection (review: wire-up regression guard)."""
    import app  # noqa: F401 — proto path

    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+psycopg2://library:library@127.0.0.1:5433/neighborhood_library",
    )
    from app.api.grpc_servicer import LibraryServicer
    from app.core.config import Settings
    from app.db.session import init_engine, ping_database

    try:
        init_engine(Settings())
        ping_database()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"PostgreSQL not available: {exc}")

    settings = Settings()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb_grpc.add_LibraryServiceServicer_to_server(LibraryServicer(settings), server)
    names = (
        pb.DESCRIPTOR.services_by_name["LibraryService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(names, server, pool=pb.DESCRIPTOR.pool)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    channel = grpc.insecure_channel(f"127.0.0.1:{port}")
    stub = pb_grpc.LibraryServiceStub(channel)
    try:
        yield stub
    finally:
        server.stop(0)
        channel.close()


def test_grpc_get_book_not_found_returns_status(grpc_stub: pb_grpc.LibraryServiceStub) -> None:
    with pytest.raises(grpc.RpcError) as ei:
        grpc_stub.GetBook(pb.GetBookRequest(id=str(uuid.uuid4())))
    assert ei.value.code() == grpc.StatusCode.NOT_FOUND
