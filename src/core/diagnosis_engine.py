from __future__ import annotations

import json
import re
from typing import Any

from src.models.diagnosis import Diagnosis, FailureTaxonomy
from src.models.findings import FindingsReport, ToolFinding, TraceFinding


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
    _SIMILAR_ID_KEYS = frozenset(
        {
            "similar_past_failure_ids",
            "similar_failure_ids",
            "past_failure_ids",
            "related_failure_ids",
        }
    )
    _SUBJECT_PATTERN = re.compile(r"subject\s*[:=]\s*([a-z0-9_-]+)", re.IGNORECASE)

    def diagnose(self, findings_report: FindingsReport | dict[str, Any]) -> Diagnosis:
        report = FindingsReport.model_validate(findings_report)
        trace_findings, tool_findings = self._partition_findings(report)
        root_cause, sub_type, explanation, confidence = self._classify(
            trace_findings, tool_findings
        )

        return Diagnosis(
            root_cause=root_cause,
            sub_type=sub_type,
            confidence=confidence,
            explanation=explanation,
            affected_subjects=self._extract_affected_subjects(trace_findings, tool_findings),
            similar_past_failure_ids=self._extract_similar_failure_ids(tool_findings),
        )

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

    def _extract_similar_failure_ids(self, tool_findings: list[ToolFinding]) -> list[str]:
        collected_ids: list[str] = []

        for finding in tool_findings:
            self._collect_similar_ids(finding.expected, collected_ids)
            self._collect_similar_ids(finding.actual, collected_ids)

        unique_ids: list[str] = []
        seen: set[str] = set()
        for failure_id in collected_ids:
            if failure_id in seen:
                continue
            unique_ids.append(failure_id)
            seen.add(failure_id)

        return unique_ids

    def _collect_similar_ids(self, payload: Any, output: list[str]) -> None:
        if isinstance(payload, dict):
            for key, value in payload.items():
                if key.lower() in self._SIMILAR_ID_KEYS:
                    output.extend(self._normalize_id_list(value))
                self._collect_similar_ids(value, output)
            return

        if isinstance(payload, list):
            for item in payload:
                self._collect_similar_ids(item, output)

    def _normalize_id_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []

        normalized_ids: list[str] = []
        for item in value:
            if not isinstance(item, str):
                continue
            candidate = item.strip()
            if candidate:
                normalized_ids.append(candidate)
        return normalized_ids


def diagnose(findings_report: FindingsReport | dict[str, Any]) -> Diagnosis:
    return DiagnosisEngine().diagnose(findings_report)
