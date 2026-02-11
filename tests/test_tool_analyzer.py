from __future__ import annotations

import json
from pathlib import Path

from src.analyzers.tool_analyzer import ToolAnalyzer


_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "traces" / "tool_calls_search.json"


def _load_trace_fixture() -> dict[str, object]:
    return json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))


def test_tool_analyzer_detects_schema_mismatch_and_wrong_tool_inference() -> None:
    analyzer = ToolAnalyzer()
    finding = analyzer.analyze(_load_trace_fixture())

    assert finding.issue == "tool_misuse_detected"
    assert finding.actual is not None

    schema_mismatches = finding.actual["schema_mismatches"]
    assert schema_mismatches
    assert schema_mismatches[0]["tool"] == "summarize_sources"
    assert finding.actual["wrong_tool_selection"] is True


def test_tool_analyzer_uses_intended_tool_metadata_when_present() -> None:
    trace = _load_trace_fixture()
    trace["metadata"] = {"intended_tool": "web_search"}

    analyzer = ToolAnalyzer()
    finding = analyzer.analyze(trace)

    assert finding.actual is not None
    assert finding.actual["wrong_tool_selection"] is True
    assert "Expected first tool 'web_search'" in finding.actual["wrong_tool_reason"]
