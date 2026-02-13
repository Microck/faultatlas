from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Literal

from src.analyzers.trace_analyzer import TraceAnalyzer
from src.analyzers.tool_analyzer import ToolAnalyzer
from src.models.findings import FindingsReport, ToolFinding, TraceFinding
from src.models.trace import TraceRecord


ExecutionMode = Literal["sequential", "parallel"]
AnalyzerResult = TraceFinding | ToolFinding
AnalyzerFn = Callable[[TraceRecord | dict[str, Any]], AnalyzerResult]


class IndagineController:
    def __init__(
        self,
        trace_analyzer: TraceAnalyzer | None = None,
        tool_analyzer: ToolAnalyzer | None = None,
        execution_mode: ExecutionMode = "sequential",
    ) -> None:
        if execution_mode not in ("sequential", "parallel"):
            raise ValueError("execution_mode must be 'sequential' or 'parallel'.")

        self._trace_analyzer = trace_analyzer or TraceAnalyzer()
        self._tool_analyzer = tool_analyzer or ToolAnalyzer()
        self._execution_mode = execution_mode
        self._analyzers: tuple[tuple[str, AnalyzerFn], ...] = (
            ("trace_analyzer", self._trace_analyzer.analyze),
            ("tool_analyzer", self._tool_analyzer.analyze),
        )

    def run_indagine(self, trace_record: TraceRecord | dict[str, Any]) -> FindingsReport:
        findings = self._run_analyzers(trace_record)
        return FindingsReport(findings=findings)

    def _run_analyzers(
        self, trace_record: TraceRecord | dict[str, Any]
    ) -> dict[str, list[AnalyzerResult]]:
        if self._execution_mode == "parallel":
            return self._run_parallel(trace_record)

        return self._run_sequential(trace_record)

    def _run_sequential(
        self, trace_record: TraceRecord | dict[str, Any]
    ) -> dict[str, list[AnalyzerResult]]:
        findings: dict[str, list[AnalyzerResult]] = {}
        for analyzer_name, analyze in self._analyzers:
            findings[analyzer_name] = [analyze(trace_record)]

        return findings

    def _run_parallel(
        self, trace_record: TraceRecord | dict[str, Any]
    ) -> dict[str, list[AnalyzerResult]]:
        findings: dict[str, list[AnalyzerResult]] = {}
        with ThreadPoolExecutor(max_workers=len(self._analyzers)) as pool:
            futures = {
                analyzer_name: pool.submit(analyze, trace_record)
                for analyzer_name, analyze in self._analyzers
            }
            for analyzer_name, _ in self._analyzers:
                findings[analyzer_name] = [futures[analyzer_name].result()]

        return findings


def run_indagine(
    trace_record: TraceRecord | dict[str, Any],
    execution_mode: ExecutionMode = "sequential",
) -> FindingsReport:
    return IndagineController(execution_mode=execution_mode).run_indagine(trace_record)
