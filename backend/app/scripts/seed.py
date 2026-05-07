"""Load sample books and members (optional loans)."""

from __future__ import annotations

from dotenv import load_dotenv

from app.core.config import Settings
from app.db.session import init_engine, session_scope
from app.services import books_service, members_service
from app.services.exceptions import ValidationError


def main() -> None:
    load_dotenv()
    settings = Settings()
    init_engine(settings)
    with session_scope() as session:
        for args in (
            dict(
                title="The Go Programming Language",
                author="Donovan & Kernighan",
                isbn="978-0134190440",
                publication_year=2015,
                total_copies=3,
            ),
            dict(
                title="Designing Data-Intensive Applications",
                author="Martin Kleppmann",
                isbn="978-1449373320",
                publication_year=2017,
                total_copies=2,
            ),
        ):
            try:
                books_service.create_book(session, **args)
            except ValidationError:
                pass
        for args in (
            dict(
                full_name="Alex Reader",
                email="alex@example.com",
                phone="+1-555-0100",
                address="123 Main St",
            ),
            dict(
                full_name="Sam Staff",
                email="sam@example.com",
                phone="+1-555-0101",
                address="",
            ),
        ):
            try:
                members_service.create_member(session, **args)
            except ValidationError:
                pass
    print("Seed complete.")


if __name__ == "__main__":
    main()
