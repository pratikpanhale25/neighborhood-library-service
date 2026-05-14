-- Neighborhood Library — canonical PostgreSQL DDL (matches SQLAlchemy models in backend/app/db).
-- Apply once per database: psql "$DATABASE_URL_LIBPQ" -v ON_ERROR_STOP=1 -f scripts/init_db.sql
-- Use postgresql://... (not postgresql+psycopg2://) with psql, or strip the +psycopg2 driver suffix.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn VARCHAR(32) NOT NULL,
    publication_year INTEGER NULL,
    total_copies INTEGER NOT NULL DEFAULT 1,
    available_copies INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT books_total_copies_min CHECK (total_copies >= 1),
    CONSTRAINT books_available_non_negative CHECK (available_copies >= 0),
    CONSTRAINT books_available_lte_total CHECK (available_copies <= total_copies),
    CONSTRAINT books_isbn_unique UNIQUE (isbn)
);

CREATE TABLE IF NOT EXISTS members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email VARCHAR(320) NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT members_email_unique UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS loans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID NOT NULL REFERENCES books (id) ON DELETE RESTRICT,
    member_id UUID NOT NULL REFERENCES members (id) ON DELETE RESTRICT,
    borrowed_at TIMESTAMPTZ NOT NULL,
    due_at TIMESTAMPTZ NULL,
    returned_at TIMESTAMPTZ NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'BORROWED',
    CONSTRAINT loans_status_chk CHECK (status IN ('BORROWED', 'RETURNED'))
);

CREATE INDEX IF NOT EXISTS ix_loans_book_id ON loans (book_id);
CREATE INDEX IF NOT EXISTS ix_loans_member_returned ON loans (member_id, returned_at);

CREATE UNIQUE INDEX IF NOT EXISTS uq_loans_active_member_book
    ON loans (member_id, book_id)
    WHERE returned_at IS NULL;

CREATE TABLE IF NOT EXISTS fines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id UUID NOT NULL REFERENCES loans (id) ON DELETE RESTRICT,
    member_id UUID NOT NULL REFERENCES members (id) ON DELETE RESTRICT,
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL,
    reason TEXT NOT NULL DEFAULT 'overdue',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ NULL,
    notes TEXT NULL,
    CONSTRAINT fines_amount_non_negative CHECK (amount_cents >= 0),
    CONSTRAINT fines_status_chk CHECK (status IN ('pending', 'paid', 'waived'))
);

CREATE INDEX IF NOT EXISTS ix_fines_member_status ON fines (member_id, status);

CREATE UNIQUE INDEX IF NOT EXISTS uq_fines_one_pending_per_loan
    ON fines (loan_id)
    WHERE status = 'pending';
