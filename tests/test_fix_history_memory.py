from __future__ import annotations

from src.models.diagnosis import Diagnosis, FailureTaxonomy
from src.models.failure import FailureEvent
from src.models.findings import FindingsReport
from src.storage.fix_history_memory import InMemoryFixHistory


def _failure_event(failure_id: str) -> FailureEvent:
    return FailureEvent(
        failure_id=failure_id,
        subject="booking",
        failure_type="validation_error",
        timestamp="2026-02-11T00:00:00Z",
        trace_id=f"trace-{failure_id}",
        error="validation failed",
        metadata={"source": "test"},
    )


def _diagnosis(root_cause: FailureTaxonomy, sub_type: str | None) -> Diagnosis:
    return Diagnosis(
        root_cause=root_cause,
        sub_type=sub_type,
        confidence=0.9,
        explanation="fixture diagnosis",
        affected_subjects=["booking"],
    )


def test_find_similar_matches_root_cause_and_sub_type() -> None:
    store = InMemoryFixHistory()
    store.record_failure(
        _failure_event("failure-1"),
        _diagnosis(FailureTaxonomy.TOOL_MISUSE, "schema_mismatch"),
    )
    store.record_failure(
        _failure_event("failure-2"),
        _diagnosis(FailureTaxonomy.TOOL_MISUSE, "wrong_tool_selection"),
    )
    store.record_failure(
        _failure_event("failure-3"),
        _diagnosis(FailureTaxonomy.HALLUCINATION, "hallucinated_metadata"),
    )
    store.record_failure(
        _failure_event("failure-4"),
        _diagnosis(FailureTaxonomy.TOOL_MISUSE, "schema_mismatch"),
    )

    similar_ids = store.find_similar(
        _diagnosis(FailureTaxonomy.TOOL_MISUSE, "schema_mismatch"),
        FindingsReport(findings={}),
        limit=5,
    )

    assert set(similar_ids) == {"failure-1", "failure-4"}
    assert len(similar_ids) == 2


def test_find_similar_respects_limit() -> None:
    store = InMemoryFixHistory()
    for failure_id in ("failure-1", "failure-2", "failure-3"):
        store.record_failure(
            _failure_event(failure_id),
            _diagnosis(FailureTaxonomy.TOOL_MISUSE, "schema_mismatch"),
        )

    similar_ids = store.find_similar(
        _diagnosis(FailureTaxonomy.TOOL_MISUSE, "schema_mismatch"),
        FindingsReport(findings={}),
        limit=2,
    )

    assert len(similar_ids) == 2
    assert set(similar_ids).issubset({"failure-1", "failure-2", "failure-3"})
