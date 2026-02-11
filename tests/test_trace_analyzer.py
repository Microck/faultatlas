from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analyzers.trace_analyzer import TraceAnalyzer


_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "traces"


def _load_trace_fixture(name: str) -> dict[str, object]:
    fixture_path = _FIXTURE_DIR / f"{name}.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("fixture_name", "expected_failure_step", "expected_total_steps"),
    [
        ("booking", 1, 1),
        ("search", 1, 1),
        ("summary", 1, 1),
    ],
)
def test_trace_analyzer_identifies_failure_step(
    fixture_name: str, expected_failure_step: int, expected_total_steps: int
) -> None:
    analyzer = TraceAnalyzer()
    trace_record = _load_trace_fixture(fixture_name)

    finding = analyzer.analyze(trace_record)

    assert finding.failure_step == expected_failure_step
    assert finding.total_steps == expected_total_steps
    assert (
        finding.failure_location
        == f"step {expected_failure_step} ({trace_record['steps'][0]['name']})"
    )


@pytest.mark.parametrize(
    ("fixture_name", "expected_phrase"),
    [
        ("booking", "15/02/2026"),
        ("search", "summarize_sources"),
        ("summary", "summarize_sources"),
    ],
)
def test_trace_analyzer_extracts_reasoning_chain(fixture_name: str, expected_phrase: str) -> None:
    analyzer = TraceAnalyzer()
    trace_record = _load_trace_fixture(fixture_name)

    finding = analyzer.analyze(trace_record)
    chain_text = " ".join(finding.reasoning_chain)

    assert finding.reasoning_chain
    assert expected_phrase in chain_text
