from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core.fix_generator import generate_fixes
from src.models.diagnosis import Diagnosis, FailureTaxonomy
from src.models.findings import FindingsReport
from src.models.fixes import FixType


_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "findings"
_FIXTURE_TAXONOMY: dict[str, FailureTaxonomy] = {
    "booking_findings": FailureTaxonomy.TOOL_MISUSE,
    "search_findings": FailureTaxonomy.PROMPT_AMBIGUITY,
    "summary_findings": FailureTaxonomy.HALLUCINATION,
    "context_overflow_findings": FailureTaxonomy.CONTEXT_OVERFLOW,
    "reasoning_error_findings": FailureTaxonomy.REASONING_ERROR,
    "coordination_findings": FailureTaxonomy.COORDINATION_FAILURE,
}


def _load_findings_fixture(name: str) -> FindingsReport:
    fixture_path = _FIXTURE_DIR / f"{name}.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    return FindingsReport.model_validate(payload)


def _diagnosis(root_cause: FailureTaxonomy) -> Diagnosis:
    return Diagnosis(
        root_cause=root_cause,
        sub_type="fixture",
        confidence=0.9,
        explanation="fixture diagnosis",
        affected_subjects=[],
        similar_past_failure_ids=[],
    )


@pytest.mark.parametrize(
    ("fixture_name", "taxonomy"),
    list(_FIXTURE_TAXONOMY.items()),
)
def test_generate_fixes_returns_at_least_one_proposal_per_taxonomy(
    fixture_name: str,
    taxonomy: FailureTaxonomy,
) -> None:
    findings_report = _load_findings_fixture(fixture_name)

    proposals = generate_fixes(_diagnosis(taxonomy), findings_report)

    assert proposals


@pytest.mark.parametrize(
    ("fixture_name", "taxonomy"),
    list(_FIXTURE_TAXONOMY.items()),
)
def test_generate_fixes_includes_unified_diff_for_each_change(
    fixture_name: str,
    taxonomy: FailureTaxonomy,
) -> None:
    findings_report = _load_findings_fixture(fixture_name)

    proposals = generate_fixes(_diagnosis(taxonomy), findings_report)

    for proposal in proposals:
        assert proposal.changes
        for change in proposal.changes:
            assert change.diff
            assert change.diff.startswith("---")
            assert "\n+++" in change.diff


def test_generate_fixes_spans_all_fix_type_categories_across_taxonomy_suite() -> None:
    emitted_fix_types: set[FixType] = set()

    for fixture_name, taxonomy in _FIXTURE_TAXONOMY.items():
        findings_report = _load_findings_fixture(fixture_name)
        proposals = generate_fixes(_diagnosis(taxonomy), findings_report)
        emitted_fix_types.update(proposal.fix_type for proposal in proposals)

    assert emitted_fix_types >= {
        FixType.PROMPT_FIX,
        FixType.TOOL_CONFIG_FIX,
        FixType.GUARDRAIL_FIX,
    }
