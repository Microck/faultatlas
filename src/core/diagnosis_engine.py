from __future__ import annotations

import json
import re
from typing import Any, Protocol

from src.models.diagnosis import Diagnosis, FailureTaxonomy
from src.models.findings import FindingsReport, ToolFinding, TraceFinding
from src.storage.fix_history_memory import InMemoryFixHistory


class _FixHistoryLookup(Protocol):
    def find_similar(
        self,
        diagnosis: Diagnosis | dict[str, Any],
        findings_report: FindingsReport | dict[str, Any],
        *,
        limit: int = 5,
    ) -> list[str]: ...


class DiagnosisEngine:
    _HALLUCINATION_MARKERS = (
        "hallucinated=true",
        "hallucinated: true",
        '"hallucinated": true',
    )
    _PROMPT_AMBIGUITY_MARKERS = (
        "missing required info",
        "missing context",
        "multiple interpretations",
        "ambiguous instruction",
        "ambiguous prompt",
    )
    _CONTEXT_OVERFLOW_MARKERS = (
        "context_overflow",
        "context_length_exceeded",
        "token limit",
        "context length",
    )
    _COORDINATION_MARKERS = (
        "coordination_failure",
        "handoff",
        "delegate",
        "agent a",
        "agent b",
    )
    _SUBJECT_PATTERN = re.compile(r"subject\s*[:=]\s*([a-z0-9_-]+)", re.IGNORECASE)

    def __init__(self, fix_history: _FixHistoryLookup | None = None) -> None:
        self._fix_history: _FixHistoryLookup = fix_history or InMemoryFixHistory()

    def diagnose(self, findings_report: FindingsReport | dict[str, Any]) -> Diagnosis:
        report = FindingsReport.model_validate(findings_report)
        trace_findings, tool_findings = self._partition_findings(report)
        root_cause, sub_type, explanation, confidence = self._classify(
            trace_findings, tool_findings
        )

        diagnosis = Diagnosis(
            root_cause=root_cause,
            sub_type=sub_type,
            confidence=confidence,
            explanation=explanation,
            affected_subjects=self._extract_affected_subjects(trace_findings, tool_findings),
            similar_past_failure_ids=[],
        )

        similar_failure_ids = self._fix_history.find_similar(diagnosis, report, limit=5)
        return diagnosis.model_copy(update={"similar_past_failure_ids": similar_failure_ids})

    def _partition_findings(
        self, findings_report: FindingsReport
    ) -> tuple[list[TraceFinding], list[ToolFinding]]:
        trace_findings: list[TraceFinding] = []
        tool_findings: list[ToolFinding] = []

        for findings in findings_report.findings.values():
            for finding in findings:
                if isinstance(finding, TraceFinding):
                    trace_findings.append(finding)
                if isinstance(finding, ToolFinding):
                    tool_findings.append(finding)

        return trace_findings, tool_findings

    def _classify(
        self, trace_findings: list[TraceFinding], tool_findings: list[ToolFinding]
    ) -> tuple[FailureTaxonomy, str | None, str, float]:
        if self._has_schema_mismatch(tool_findings):
            return (
                FailureTaxonomy.TOOL_MISUSE,
                "schema_mismatch",
                "Tool invocation parameters violate the registered tool schema.",
                0.9,
            )

        if self._has_wrong_tool_flag(tool_findings):
            return (
                FailureTaxonomy.TOOL_MISUSE,
                "wrong_tool_selection",
                "Tool execution selected the wrong tool for the requested operation.",
                0.9,
            )

        combined_text = self._combined_text(trace_findings, tool_findings)

        hallucination_marker = self._first_marker(combined_text, self._HALLUCINATION_MARKERS)
        if hallucination_marker is not None:
            return (
                FailureTaxonomy.HALLUCINATION,
                "hallucinated_metadata",
                "Trace metadata includes hallucination marker 'hallucinated=true'.",
                0.9,
            )

        prompt_marker = self._first_marker(combined_text, self._PROMPT_AMBIGUITY_MARKERS)
        if prompt_marker is not None:
            return (
                FailureTaxonomy.PROMPT_AMBIGUITY,
                prompt_marker,
                "Trace indicates missing required context or multiple valid prompt interpretations.",
                0.9,
            )

        context_marker = self._first_marker(combined_text, self._CONTEXT_OVERFLOW_MARKERS)
        if context_marker is not None:
            return (
                FailureTaxonomy.CONTEXT_OVERFLOW,
                context_marker,
                "Trace includes deterministic context overflow markers (token/context limits).",
                0.9,
            )

        coordination_marker = self._first_marker(combined_text, self._COORDINATION_MARKERS)
        if coordination_marker is not None:
            return (
                FailureTaxonomy.COORDINATION_FAILURE,
                coordination_marker,
                "Trace includes coordination or handoff failure signals between agents.",
                0.9,
            )

        return (
            FailureTaxonomy.REASONING_ERROR,
            "fallback",
            "No stronger deterministic signal matched; classified as reasoning error.",
            0.6,
        )

    def _combined_text(
        self, trace_findings: list[TraceFinding], tool_findings: list[ToolFinding]
    ) -> str:
        return " ".join(self._raw_text_blobs(trace_findings, tool_findings)).lower()

    def _raw_text_blobs(
        self, trace_findings: list[TraceFinding], tool_findings: list[ToolFinding]
    ) -> list[str]:
        blobs: list[str] = []

        for finding in trace_findings:
            if finding.failure_location:
                blobs.append(finding.failure_location)
            if finding.error:
                blobs.append(finding.error)
            blobs.extend(finding.reasoning_chain)

        for finding in tool_findings:
            if finding.tool:
                blobs.append(finding.tool)
            if finding.issue:
                blobs.append(finding.issue)
            if finding.expected is not None:
                blobs.append(json.dumps(finding.expected, sort_keys=True))
            if finding.actual is not None:
                blobs.append(json.dumps(finding.actual, sort_keys=True))

        return blobs

    def _first_marker(self, text: str, markers: tuple[str, ...]) -> str | None:
        for marker in markers:
            if marker in text:
                return marker
        return None

    def _has_schema_mismatch(self, tool_findings: list[ToolFinding]) -> bool:
        for finding in tool_findings:
            if not isinstance(finding.actual, dict):
                continue
            mismatches = finding.actual.get("schema_mismatches")
            if isinstance(mismatches, list) and len(mismatches) > 0:
                return True
        return False

    def _has_wrong_tool_flag(self, tool_findings: list[ToolFinding]) -> bool:
        for finding in tool_findings:
            if not isinstance(finding.actual, dict):
                continue
            if finding.actual.get("wrong_tool_selection") is True:
                return True
        return False

    def _extract_affected_subjects(
        self, trace_findings: list[TraceFinding], tool_findings: list[ToolFinding]
    ) -> list[str]:
        subjects: list[str] = []
        blobs = self._raw_text_blobs(trace_findings, tool_findings)

        for blob in blobs:
            for match in self._SUBJECT_PATTERN.findall(blob):
                normalized = match.lower()
                if normalized not in subjects:
                    subjects.append(normalized)

        if subjects:
            return subjects

        combined = " ".join(blobs).lower()
        for known_subject in ("booking", "search", "summary"):
            if known_subject in combined and known_subject not in subjects:
                subjects.append(known_subject)

        return subjects


def diagnose(findings_report: FindingsReport | dict[str, Any]) -> Diagnosis:
    return DiagnosisEngine().diagnose(findings_report)
