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


def test_list_books_pagination_no_duplicates(client: TestClient) -> None:
    """Walk ``next_page_token`` until exhausted; IDs must not repeat (review: pagination)."""
    mark = uuid.uuid4().hex[:8]
    created: list[str] = []
    for i in range(5):
        isbn = f"pg-{uuid.uuid4().hex[:12]}"
        r = client.post(
            "/books",
            json={
                "title": f"PgMark-{mark}-{i}",
                "author": "Pager",
                "isbn": isbn,
                "total_copies": 1,
            },
        )
        assert r.status_code == 201, r.text
        created.append(r.json()["id"])

    seen: set[str] = set()
    token = ""
    q = f"PgMark-{mark}"
    while True:
        r = client.get("/books", params={"page_size": 2, "page_token": token, "query": q})
        assert r.status_code == 200, r.text
        data = r.json()
        for item in data["items"]:
            bid = item["id"]
            assert bid not in seen
            seen.add(bid)
        token = data.get("next_page_token") or ""
        if not token:
            break
    assert seen == set(created)


def test_concurrent_borrow_last_copy_one_wins(client: TestClient) -> None:
    """Two borrowers racing for one copy: one 201, one 409; inventory stays consistent (review)."""
    import concurrent.futures

    isbn = f"race-{uuid.uuid4().hex[:12]}"
    br = client.post(
        "/books",
        json={
            "title": "Race Book",
            "author": "Racer",
            "isbn": isbn,
            "total_copies": 1,
        },
    )
    assert br.status_code == 201, br.text
    book_id = br.json()["id"]

    emails = [f"a{uuid.uuid4().hex[:8]}@e.com", f"b{uuid.uuid4().hex[:8]}@e.com"]
    member_ids: list[str] = []
    for em in emails:
        mr = client.post(
            "/members",
            json={"name": "R", "email": em, "phone": "1", "address": None},
        )
        assert mr.status_code == 201, mr.text
        member_ids.append(mr.json()["id"])

    codes: list[int] = []

    def borrow(mid: str) -> None:
        resp = client.post(
            "/borrow",
            json={"member_id": mid, "book_id": book_id},
        )
        codes.append(resp.status_code)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(borrow, member_ids))

    assert sorted(codes) == [201, 409]
    g = client.get(f"/books/{book_id}")
    assert g.json()["available_copies"] == 0


def test_overdue_return_then_pay_and_separate_waive(client: TestClient) -> None:
    """Overdue return creates a pending fine; pay/waive transitions succeed (review: state machine)."""
    from datetime import datetime, timedelta, timezone

    isbn = f"fine-{uuid.uuid4().hex[:12]}"
    br = client.post(
        "/books",
        json={
            "title": "Fine Book",
            "author": "F",
            "isbn": isbn,
            "total_copies": 1,
        },
    )
    assert br.status_code == 201, br.text
    book_id = br.json()["id"]

    em1 = f"p{uuid.uuid4().hex[:8]}@e.com"
    m1 = client.post("/members", json={"name": "Payer", "email": em1, "phone": "1", "address": None})
    assert m1.status_code == 201, m1.text
    payer_id = m1.json()["id"]
    due = datetime.now(timezone.utc) - timedelta(days=5)
    bor = client.post(
        "/borrow",
        json={"member_id": payer_id, "book_id": book_id, "due_date": due.isoformat()},
    )
    assert bor.status_code == 201, bor.text
    loan_id = bor.json()["id"]
    ret = client.post("/return", json={"loan_id": loan_id})
    assert ret.status_code == 200, ret.text

    fr = client.get("/fines", params={"member_id": payer_id, "status": "pending"})
    assert fr.status_code == 200, fr.text
    fines = fr.json()["items"]
    assert len(fines) >= 1
    fine_id = fines[0]["id"]
    pr = client.post(f"/fines/{fine_id}/pay", json={"notes": "paid test"})
    assert pr.status_code == 200, pr.text
    assert pr.json()["status"] == "paid"

    isbn2 = f"fine2-{uuid.uuid4().hex[:12]}"
    br2 = client.post(
        "/books",
        json={"title": "Fine2", "author": "F", "isbn": isbn2, "total_copies": 1},
    )
    assert br2.status_code == 201, br2.text
    book2 = br2.json()["id"]
    em2 = f"w{uuid.uuid4().hex[:8]}@e.com"
    m2 = client.post("/members", json={"name": "Waive", "email": em2, "phone": "1", "address": None})
    assert m2.status_code == 201, m2.text
    mid2 = m2.json()["id"]
    due2 = datetime.now(timezone.utc) - timedelta(days=3)
    loan2 = client.post(
        "/borrow",
        json={"member_id": mid2, "book_id": book2, "due_date": due2.isoformat()},
    )
    assert loan2.status_code == 201, loan2.text
    ret2 = client.post("/return", json={"loan_id": loan2.json()["id"]})
    assert ret2.status_code == 200, ret2.text
    fr2 = client.get("/fines", params={"member_id": mid2, "status": "pending"})
    fid2 = fr2.json()["items"][0]["id"]
    wr = client.post(f"/fines/{fid2}/waive", json={"notes": "waive test"})
    assert wr.status_code == 200, wr.text
    assert wr.json()["status"] == "waived"
