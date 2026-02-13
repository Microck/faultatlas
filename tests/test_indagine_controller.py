from __future__ import annotations

import json
from pathlib import Path

from src.core.indagine_controller import run_indagine
from src.core.indagine_pipeline import IndaginePipeline


_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "traces"


def _load_trace_fixture(name: str) -> dict[str, object]:
    fixture_path = _FIXTURE_DIR / f"{name}.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def test_run_indagine_returns_unified_findings_report_shape() -> None:
    report = run_indagine(_load_trace_fixture("booking"))

    assert set(report.findings.keys()) == {"trace_analyzer", "tool_analyzer"}

    trace_findings = report.findings["trace_analyzer"]
    assert trace_findings

    trace_finding = trace_findings[0]
    assert trace_finding.failure_step == 1
    assert trace_finding.reasoning_chain


def test_run_indagine_reports_tool_issue_for_search_agent_fixture() -> None:
    report = run_indagine(_load_trace_fixture("tool_calls_search"))

    tool_findings = report.findings["tool_analyzer"]
    assert tool_findings

    tool_finding = tool_findings[0]
    assert tool_finding.issue == "tool_misuse_detected"
    assert tool_finding.actual is not None

    issue_count = len(tool_finding.actual["schema_mismatches"])
    if tool_finding.actual["wrong_tool_selection"]:
        issue_count += 1

    assert issue_count >= 1


def test_indagine_pipeline_uses_injected_trace_store() -> None:
    trace_record = _load_trace_fixture("booking")
    requested_failure_ids: list[str] = []

    class StubTraceStore:
        def get_trace(self, failure_id: str) -> dict[str, object]:
            requested_failure_ids.append(failure_id)
            return {"trace_record": trace_record}

    pipeline = IndaginePipeline(trace_store=StubTraceStore())
    report = pipeline.run("booking-failure")

    assert requested_failure_ids == ["booking-failure"]
    assert set(report.findings.keys()) == {"trace_analyzer", "tool_analyzer"}
