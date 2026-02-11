from __future__ import annotations

import json
from typing import Any

from src.models.findings import TraceFinding
from src.models.trace import TraceRecord, TraceStep, TraceToolCall


class TraceAnalyzer:
    def analyze(self, trace_record: TraceRecord | dict[str, Any]) -> TraceFinding:
        trace = TraceRecord.model_validate(trace_record)
        total_steps = len(trace.steps)
        failed_index = self._find_failure_index(trace.steps)

        failure_step: int | None = None
        failure_location: str | None = None
        error: str | None = None

        if failed_index is not None:
            failed_step = trace.steps[failed_index]
            failure_step = failed_index + 1
            failure_location = f"step {failure_step} ({failed_step.name})"
            error = failed_step.error

        return TraceFinding(
            failure_step=failure_step,
            total_steps=total_steps,
            failure_location=failure_location,
            error=error,
            reasoning_chain=self._extract_reasoning_chain(trace.steps),
        )

    def _find_failure_index(self, steps: list[TraceStep]) -> int | None:
        for index, step in enumerate(steps):
            if step.error:
                return index
            if step.kind == "validation_error":
                return index
            if "validation_error" in step.name:
                return index

        return None

    def _extract_reasoning_chain(self, steps: list[TraceStep]) -> list[str]:
        explicit_chain: list[str] = []
        for step in steps:
            if step.thought:
                explicit_chain.append(step.thought)
            if step.decision:
                explicit_chain.append(step.decision)

        if explicit_chain:
            return explicit_chain

        derived_chain: list[str] = []
        for step in steps:
            for tool_call in self._tool_calls_for_step(step):
                args_repr = json.dumps(tool_call.args, sort_keys=True)
                derived_chain.append(f"{step.name}: call {tool_call.tool} with args {args_repr}")

            if step.input:
                input_repr = json.dumps(step.input, sort_keys=True)
                derived_chain.append(f"{step.name}: input {input_repr}")

            if step.error:
                derived_chain.append(f"{step.name}: error {step.error}")

        return derived_chain

    def _tool_calls_for_step(self, step: TraceStep) -> list[TraceToolCall]:
        if step.tool_calls:
            return step.tool_calls

        if not step.output:
            return []

        raw_tool_calls = step.output.get("tool_calls")
        if not isinstance(raw_tool_calls, list):
            return []

        tool_calls: list[TraceToolCall] = []
        for raw_tool_call in raw_tool_calls:
            if not isinstance(raw_tool_call, dict):
                continue
            tool_calls.append(TraceToolCall.model_validate(raw_tool_call))

        return tool_calls


def analyze(trace_record: TraceRecord | dict[str, Any]) -> TraceFinding:
    return TraceAnalyzer().analyze(trace_record)
