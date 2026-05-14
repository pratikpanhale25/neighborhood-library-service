"""Map generated protobuf enums to service-layer labels (no raw int literals).

Code review: magic integers for proto enum values were brittle; comparing against
``library_pb2`` symbols keeps filters aligned with ``library.proto`` when values change.
"""

from __future__ import annotations

from typing import Literal, Optional

from library.v1 import library_pb2 as pb

LoanFilterSQL = Literal["active", "returned", "all", "overdue"]


def loan_filter_proto_to_sql(filter_val: int) -> LoanFilterSQL:
    """Map ``LoanFilter`` wire value to the SQL strategy used by ``list_loans``."""
    if filter_val == pb.LoanFilter.LOAN_FILTER_RETURNED_ONLY:
        return "returned"
    if filter_val == pb.LoanFilter.LOAN_FILTER_ALL:
        return "all"
    if filter_val == pb.LoanFilter.LOAN_FILTER_OVERDUE_ONLY:
        return "overdue"
    # UNSPECIFIED and ACTIVE_ONLY both mean “active-only” list semantics (prior behavior).
    return "active"


def fine_status_filter_proto_to_sql(filter_val: int) -> str:
    """Map ``FineStatusFilter`` to persisted ``fines.status`` or ``any`` (no status clause)."""
    if filter_val == pb.FineStatusFilter.FINE_STATUS_FILTER_PENDING:
        return "pending"
    if filter_val == pb.FineStatusFilter.FINE_STATUS_FILTER_PAID:
        return "paid"
    if filter_val == pb.FineStatusFilter.FINE_STATUS_FILTER_WAIVED:
        return "waived"
    if filter_val == pb.FineStatusFilter.FINE_STATUS_FILTER_ANY:
        return "any"
    # UNSPECIFIED: same as ANY so older clients without the field behave as today.
    return "any"


def loan_filter_from_rest_status(status: Optional[str]) -> int:
    """Translate REST ``status`` query param to ``LoanFilter`` for shared service logic."""
    s = (status or "active").lower().strip()
    if s == "returned":
        return int(pb.LoanFilter.LOAN_FILTER_RETURNED_ONLY)
    if s == "all":
        return int(pb.LoanFilter.LOAN_FILTER_ALL)
    if s == "overdue":
        return int(pb.LoanFilter.LOAN_FILTER_OVERDUE_ONLY)
    return int(pb.LoanFilter.LOAN_FILTER_ACTIVE_ONLY)


def fine_status_filter_from_rest_status(status: Optional[str]) -> int:
    """Translate REST ``status`` query param to ``FineStatusFilter``."""
    s = (status or "any").lower().strip()
    if s == "pending":
        return int(pb.FineStatusFilter.FINE_STATUS_FILTER_PENDING)
    if s == "paid":
        return int(pb.FineStatusFilter.FINE_STATUS_FILTER_PAID)
    if s == "waived":
        return int(pb.FineStatusFilter.FINE_STATUS_FILTER_WAIVED)
    return int(pb.FineStatusFilter.FINE_STATUS_FILTER_ANY)
