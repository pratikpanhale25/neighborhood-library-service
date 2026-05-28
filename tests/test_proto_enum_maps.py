"""Unit tests for protobuf enum → service-layer mappings."""

from __future__ import annotations

from library.v1 import library_pb2 as pb

from app.services.proto_enum_maps import (
    fine_status_filter_from_rest_status,
    fine_status_filter_proto_to_sql,
    loan_filter_from_rest_status,
    loan_filter_proto_to_sql,
)


def test_loan_filter_proto_matches_prior_semantics() -> None:
    """Regression: SQL labels must stay aligned with historical int-based mapping."""
    assert loan_filter_proto_to_sql(int(pb.LoanFilter.LOAN_FILTER_UNSPECIFIED)) == "active"
    assert loan_filter_proto_to_sql(int(pb.LoanFilter.LOAN_FILTER_ACTIVE_ONLY)) == "active"
    assert loan_filter_proto_to_sql(int(pb.LoanFilter.LOAN_FILTER_RETURNED_ONLY)) == "returned"
    assert loan_filter_proto_to_sql(int(pb.LoanFilter.LOAN_FILTER_ALL)) == "all"
    assert loan_filter_proto_to_sql(int(pb.LoanFilter.LOAN_FILTER_OVERDUE_ONLY)) == "overdue"


def test_fine_status_filter_proto_matches_prior_semantics() -> None:
    assert fine_status_filter_proto_to_sql(int(pb.FineStatusFilter.FINE_STATUS_FILTER_UNSPECIFIED)) == "any"
    assert fine_status_filter_proto_to_sql(int(pb.FineStatusFilter.FINE_STATUS_FILTER_PENDING)) == "pending"
    assert fine_status_filter_proto_to_sql(int(pb.FineStatusFilter.FINE_STATUS_FILTER_PAID)) == "paid"
    assert fine_status_filter_proto_to_sql(int(pb.FineStatusFilter.FINE_STATUS_FILTER_WAIVED)) == "waived"
    assert fine_status_filter_proto_to_sql(int(pb.FineStatusFilter.FINE_STATUS_FILTER_ANY)) == "any"


def test_rest_status_strings_map_to_proto_ints() -> None:
    """REST adapters should emit the same ints gRPC clients send for each filter."""
    assert loan_filter_from_rest_status("active") == int(pb.LoanFilter.LOAN_FILTER_ACTIVE_ONLY)
    assert loan_filter_from_rest_status("returned") == int(pb.LoanFilter.LOAN_FILTER_RETURNED_ONLY)
    assert fine_status_filter_from_rest_status("pending") == int(pb.FineStatusFilter.FINE_STATUS_FILTER_PENDING)
