from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core.diagnosis_engine import DiagnosisEngine
from src.models.diagnosis import FailureTaxonomy
from src.models.findings import FindingsReport


_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "findings"
_FIXTURE_EXPECTED_ROOT_CAUSE: dict[str, FailureTaxonomy] = {
    "booking_findings": FailureTaxonomy.TOOL_MISUSE,
    "search_findings": FailureTaxonomy.PROMPT_AMBIGUITY,
    "summary_findings": FailureTaxonomy.HALLUCINATION,
    "context_overflow_findings": FailureTaxonomy.CONTEXT_OVERFLOW,
    "coordination_findings": FailureTaxonomy.COORDINATION_FAILURE,
    "reasoning_error_findings": FailureTaxonomy.REASONING_ERROR,
}


def _load_findings_fixture(name: str) -> dict[str, object]:
    fixture_path = _FIXTURE_DIR / f"{name}.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def _diagnose_fixture(name: str) -> object:
    findings_report = FindingsReport.model_validate(_load_findings_fixture(name))
    return DiagnosisEngine().diagnose(findings_report)


@pytest.mark.parametrize(
    ("fixture_name", "expected_root_cause"),
    list(_FIXTURE_EXPECTED_ROOT_CAUSE.items()),
)
def test_diagnosis_engine_classifies_fixture_by_deterministic_signals(
    fixture_name: str, expected_root_cause: FailureTaxonomy
) -> None:
    diagnosis = _diagnose_fixture(fixture_name)

    assert diagnosis.root_cause == expected_root_cause
    assert diagnosis.explanation
    assert 0.0 <= diagnosis.confidence <= 1.0


def test_diagnosis_engine_emits_every_taxonomy_type() -> None:
    emitted_taxonomy = {
        _diagnose_fixture(fixture_name).root_cause for fixture_name in _FIXTURE_EXPECTED_ROOT_CAUSE
    }

    assert emitted_taxonomy == set(FailureTaxonomy)


@pytest.mark.parametrize("fixture_name", list(_FIXTURE_EXPECTED_ROOT_CAUSE.keys()))
def test_diagnosis_engine_keeps_similar_failure_links_consistent(fixture_name: str) -> None:
    diagnosis = _diagnose_fixture(fixture_name)
    payload = diagnosis.model_dump()

    assert "similar_past_failure_ids" in payload
    assert "similar_past_failures" in payload
    assert diagnosis.similar_past_failures == len(diagnosis.similar_past_failure_ids)
