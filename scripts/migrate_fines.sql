-- Apply on existing DBs that already ran init_db.sql before fines existed.

CREATE TABLE IF NOT EXISTS fines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id UUID NOT NULL REFERENCES loans (id) ON DELETE RESTRICT,
    member_id UUID NOT NULL REFERENCES members (id) ON DELETE RESTRICT,
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    currency TEXT NOT NULL DEFAULT 'USD',
    status TEXT NOT NULL CHECK (status IN ('pending', 'paid', 'waived')),
    reason TEXT NOT NULL DEFAULT 'overdue',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    notes TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS fines_one_pending_per_loan
    ON fines (loan_id)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS fines_member_status_idx ON fines (member_id, status);
CREATE INDEX IF NOT EXISTS fines_loan_idx ON fines (loan_id);
