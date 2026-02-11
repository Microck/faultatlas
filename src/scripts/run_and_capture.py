from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

from opentelemetry import trace

from src.core.failure_detector import run_with_failure_detection
from src.core.tracing import configure_tracing
from src.storage.trace_store import TraceStore
from src.subjects.booking_agent import run_booking_scenario
from src.subjects.search_agent import run_search_scenario
from src.subjects.summary_agent import run_summary_scenario


SubjectRunner = Callable[[], dict[str, Any]]

SUBJECT_RUNNERS: tuple[tuple[str, SubjectRunner], ...] = (
    ("booking", run_booking_scenario),
    ("search", run_search_scenario),
    ("summary", run_summary_scenario),
)


def _capture_subject(
    trace_store: TraceStore,
    subject_name: str,
    runner: SubjectRunner,
    timeout_s: float,
) -> dict[str, Any]:
    failure_event, trace_record = run_with_failure_detection(
        subject_name, runner, timeout_s=timeout_s
    )
    trace_store.store_trace(failure_event, trace_record)

    recovered = trace_store.get_trace(failure_event.failure_id)
    recovered_failure = recovered["failure_event"]
    recovered_trace = recovered["trace_record"]

    return {
        "failure_id": recovered_failure["failure_id"],
        "subject": recovered_failure["subject"],
        "failure_type": recovered_failure["failure_type"],
        "steps_count": len(recovered_trace.get("steps", [])),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run subjects and persist traces by failure_id.")
    parser.add_argument("--store", choices=["memory", "cosmos"], default="memory")
    parser.add_argument("--timeout-s", type=float, default=5.0)
    args = parser.parse_args(argv)

    configure_tracing()
    tracer = trace.get_tracer(__name__)
    trace_store = TraceStore(backend=args.store)

    for subject_name, runner in SUBJECT_RUNNERS:
        with tracer.start_as_current_span(f"run_and_capture:{subject_name}"):
            summary = _capture_subject(trace_store, subject_name, runner, args.timeout_s)
            json.dump(summary, sys.stdout)
            sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
