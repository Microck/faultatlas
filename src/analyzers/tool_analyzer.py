from __future__ import annotations

from typing import Any

from src.models.findings import ToolFinding
from src.models.trace import TraceRecord
from src.tools.schema_registry import SchemaRegistry


class ToolAnalyzer:
    def __init__(self, schema_registry: SchemaRegistry | None = None) -> None:
        self._schema_registry = schema_registry or SchemaRegistry()

    def analyze(self, trace_record: TraceRecord | dict[str, Any]) -> ToolFinding:
        trace_payload = self._as_trace_payload(trace_record)
        tool_calls = self._extract_tool_calls(trace_payload)

        schema_mismatches: list[dict[str, Any]] = []
        for tool_call in tool_calls:
            for mismatch in self._schema_registry.validate(
                tool_call["tool_name"], tool_call["args"]
            ):
                schema_mismatches.append(
                    {
                        "step": tool_call["step"],
                        "step_name": tool_call["step_name"],
                        "tool": tool_call["tool_name"],
                        "code": mismatch.get("code"),
                        "message": mismatch.get("message"),
                        "path": mismatch.get("path"),
                        "details": mismatch.get("details"),
                    }
                )

        wrong_tool = self._detect_wrong_tool(trace_payload, tool_calls)
        issue = None
        if schema_mismatches or wrong_tool["flagged"]:
            issue = "tool_misuse_detected"

        return ToolFinding(
            tool=tool_calls[0]["tool_name"] if tool_calls else None,
            issue=issue,
            expected=wrong_tool["expected"],
            actual={
                "tool_calls": tool_calls,
                "schema_mismatches": schema_mismatches,
                "wrong_tool_selection": wrong_tool["flagged"],
                "wrong_tool_reason": wrong_tool["reason"],
            },
        )

    def _as_trace_payload(self, trace_record: TraceRecord | dict[str, Any]) -> dict[str, Any]:
        if isinstance(trace_record, TraceRecord):
            return trace_record.model_dump()
        if isinstance(trace_record, dict):
            return trace_record
        raise TypeError("trace_record must be a TraceRecord or dictionary")

    def _extract_tool_calls(self, trace_payload: dict[str, Any]) -> list[dict[str, Any]]:
        steps = trace_payload.get("steps")
        if not isinstance(steps, list):
            return []

        tool_calls: list[dict[str, Any]] = []
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                continue

            step_name = str(step.get("name") or f"step_{index}")
            for raw_call in self._tool_calls_for_step(step):
                if not isinstance(raw_call, dict):
                    continue

                raw_name = raw_call.get("tool")
                tool_name = raw_name.strip() if isinstance(raw_name, str) else ""
                if not tool_name:
                    continue

                args = raw_call.get("args")
                if not isinstance(args, dict):
                    args = {}

                tool_calls.append(
                    {
                        "step": index,
                        "step_name": step_name,
                        "tool_name": tool_name,
                        "args": args,
                    }
                )

        return tool_calls

    def _tool_calls_for_step(self, step: dict[str, Any]) -> list[dict[str, Any]]:
        direct_tool_calls = step.get("tool_calls")
        if isinstance(direct_tool_calls, list):
            return [call for call in direct_tool_calls if isinstance(call, dict)]

        output = step.get("output")
        if not isinstance(output, dict):
            return []

        output_tool_calls = output.get("tool_calls")
        if not isinstance(output_tool_calls, list):
            return []

        return [call for call in output_tool_calls if isinstance(call, dict)]

    def _detect_wrong_tool(
        self, trace_payload: dict[str, Any], tool_calls: list[dict[str, Any]]
    ) -> dict[str, Any]:
        first_tool = tool_calls[0]["tool_name"] if tool_calls else None
        intended_tool = self._intended_tool(trace_payload)

        if intended_tool and first_tool and first_tool != intended_tool:
            return {
                "flagged": True,
                "reason": (
                    f"Expected first tool '{intended_tool}' from trace metadata but called "
                    f"'{first_tool}'."
                ),
                "expected": {"intended_tool": intended_tool},
            }

        if (
            intended_tool is None
            and first_tool == "summarize_sources"
            and self._is_search_request(trace_payload)
        ):
            return {
                "flagged": True,
                "reason": (
                    "Search-like request called 'summarize_sources' before any search tool."
                ),
                "expected": {"first_tool": "web_search"},
            }

        expected: dict[str, Any] | None = None
        if intended_tool:
            expected = {"intended_tool": intended_tool}

        return {
            "flagged": False,
            "reason": None,
            "expected": expected,
        }

    def _intended_tool(self, trace_payload: dict[str, Any]) -> str | None:
        metadata = trace_payload.get("metadata")
        if isinstance(metadata, dict):
            raw_tool = metadata.get("intended_tool")
            if isinstance(raw_tool, str) and raw_tool.strip():
                return raw_tool.strip()

        raw_tool = trace_payload.get("intended_tool")
        if isinstance(raw_tool, str) and raw_tool.strip():
            return raw_tool.strip()

        return None

    def _is_search_request(self, trace_payload: dict[str, Any]) -> bool:
        phrases = self._collect_prompt_phrases(trace_payload)
        combined = " ".join(phrases).lower()
        return "search" in combined or "find" in combined

    def _collect_prompt_phrases(self, trace_payload: dict[str, Any]) -> list[str]:
        phrases: list[str] = []

        top_level_input = trace_payload.get("input")
        if isinstance(top_level_input, dict):
            for value in top_level_input.values():
                if isinstance(value, str):
                    phrases.append(value)

        steps = trace_payload.get("steps")
        if isinstance(steps, list):
            for step in steps:
                if not isinstance(step, dict):
                    continue
                step_input = step.get("input")
                if not isinstance(step_input, dict):
                    continue
                for value in step_input.values():
                    if isinstance(value, str):
                        phrases.append(value)

        return phrases


def analyze(trace_record: TraceRecord | dict[str, Any]) -> ToolFinding:
    return ToolAnalyzer().analyze(trace_record)
