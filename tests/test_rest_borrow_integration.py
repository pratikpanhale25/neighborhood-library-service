"""Integration test: borrow and return via REST (requires PostgreSQL)."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def client() -> TestClient:
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+psycopg2://library:library@127.0.0.1:5433/neighborhood_library",
    )
    from app.api.app_factory import create_app
    from app.core.config import Settings
    from app.db.session import init_engine, ping_database

    try:
        init_engine(Settings())
        ping_database()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"PostgreSQL not available for integration tests: {exc}")
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_borrow_and_return_flow(client: TestClient) -> None:
    isbn = f"test-{uuid.uuid4().hex[:12]}"
    br = client.post(
        "/books",
        json={
            "title": "Integration Book",
            "author": "Tester",
            "isbn": isbn,
            "total_copies": 2,
        },
    )
    assert br.status_code == 201, br.text
    book_id = br.json()["id"]

    em = f"u{uuid.uuid4().hex[:10]}@example.com"
    mr = client.post(
        "/members",
        json={"name": "Borrower", "email": em, "phone": "555", "address": None},
    )
    assert mr.status_code == 201, mr.text
    member_id = mr.json()["id"]

    bor = client.post(
        "/borrow",
        json={"member_id": member_id, "book_id": book_id},
    )
    assert bor.status_code == 201, bor.text
    loan_id = bor.json()["id"]

    ret = client.post("/return", json={"loan_id": loan_id})
    assert ret.status_code == 200, ret.text

    g = client.get(f"/books/{book_id}")
    assert g.json()["available_copies"] == 2
