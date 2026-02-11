from __future__ import annotations

import json
import traceback
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from datetime import datetime, timezone
from typing import Any, Callable, Literal

from opentelemetry import trace
from opentelemetry.trace import Span
from opentelemetry.trace.status import Status, StatusCode

from src.models.failure import FailureEvent, FailureType
from src.models.trace_record import TraceRecord, TraceStep
from src.tools.registry import ToolValidationError


ScenarioFn = Callable[[], dict[str, Any]]
TraceStatus = Literal["failed", "hallucinated", "passed"]


def _now_rfc3339() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _build_failure_id(subject_name: str, started_at: str) -> str:
    token = (
        started_at.replace("-", "")
        .replace(":", "")
        .replace("T", "")
        .replace(".", "")
        .replace("Z", "")
    )
    return f"{subject_name}-{token}"


def _trace_id_from_span(span: Span) -> str | None:
    span_context = span.get_span_context()
    if not span_context or span_context.trace_id == 0:
        return None

    return f"{span_context.trace_id:032x}"


def _as_json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return json.loads(json.dumps(value, default=str))

    return {"raw_result": str(value)}


def _classify_result(
    result: dict[str, Any],
) -> tuple[TraceStatus, FailureType, str, dict[str, Any]]:
    result_status = str(result.get("status", "passed")).lower()

    if result_status == "hallucinated" or bool(result.get("hallucinated")):
        message = str(result.get("false_claim") or "Hallucination marker detected.")
        return (
            "hallucinated",
            "hallucination_flag",
            message,
            {"status": "hallucinated", "hallucinated": True},
        )

    if result_status == "failed":
        error_payload = result.get("error")
        failure_type: FailureType = "exception"
        details: dict[str, Any] = {"status": "failed"}

        if isinstance(error_payload, dict):
            details["error"] = error_payload
            if error_payload.get("code") == "schema_validation_failed":
                failure_type = "validation_error"
            message = str(
                error_payload.get("message")
                or error_payload.get("code")
                or "Subject reported failed status."
            )
        else:
            message = str(error_payload or "Subject reported failed status.")

        return "failed", failure_type, message, details

    return "passed", "none", "", {"status": "passed"}


def run_with_failure_detection(
    subject_name: str,
    fn: ScenarioFn,
    *,
    timeout_s: float,
) -> tuple[FailureEvent, dict[str, Any]]:
    started_at = _now_rfc3339()
    failure_id = _build_failure_id(subject_name, started_at)
    tracer = trace.get_tracer(__name__)

    trace_id: str | None = None
    status: TraceStatus = "passed"
    failure_type: FailureType = "none"
    error_message = ""
    metadata: dict[str, Any] = {}
    steps: list[TraceStep] = []

    with tracer.start_as_current_span(f"run_subject:{subject_name}") as span:
        trace_id = _trace_id_from_span(span)
        span.set_attribute("faultatlas.subject", subject_name)
        span.set_attribute("faultatlas.failure_id", failure_id)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fn)
            try:
                raw_result = future.result(timeout=timeout_s)
            except FuturesTimeoutError:
                future.cancel()
                status = "failed"
                failure_type = "timeout"
                error_message = f"Execution exceeded timeout after {timeout_s}s."
                metadata = {"timeout_s": timeout_s}
                timeout_error = TimeoutError(error_message)
                span.record_exception(timeout_error)
                span.set_status(Status(StatusCode.ERROR, error_message))
                steps.append(
                    TraceStep(
                        name="subject_timeout",
                        kind="exception",
                        input=None,
                        output=None,
                        error=error_message,
                    )
                )
            except ToolValidationError as exc:
                status = "failed"
                failure_type = "validation_error"
                error_message = exc.message
                metadata = exc.to_dict()
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, error_message))
                steps.append(
                    TraceStep(
                        name="subject_validation",
                        kind="validation_error",
                        input={"tool": exc.tool, "details": exc.details},
                        output=None,
                        error=error_message,
                    )
                )
            except Exception as exc:
                status = "failed"
                failure_type = "exception"
                error_message = f"{type(exc).__name__}: {exc}"
                metadata = {
                    "exception_type": type(exc).__name__,
                    "traceback": traceback.format_exc(),
                }
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, error_message))
                steps.append(
                    TraceStep(
                        name="subject_exception",
                        kind="exception",
                        input=None,
                        output=None,
                        error=error_message,
                    )
                )
            else:
                result = _as_json_object(raw_result)
                status, failure_type, error_message, metadata = _classify_result(result)
                span.set_attribute("faultatlas.status", status)
                if failure_type != "none":
                    span.set_attribute("faultatlas.failure_type", failure_type)
                steps.append(
                    TraceStep(
                        name="subject_result",
                        kind="model_output",
                        input=result.get("input")
                        if isinstance(result.get("input"), dict)
                        else None,
                        output=result,
                        error=error_message or None,
                    )
                )

    ended_at = _now_rfc3339()
    trace_record = TraceRecord(
        failure_id=failure_id,
        subject=subject_name,
        status=status,
        started_at=started_at,
        ended_at=ended_at,
        steps=steps,
    )

    failure_event = FailureEvent(
        failure_id=failure_id,
        subject=subject_name,
        failure_type=failure_type,
        timestamp=ended_at,
        trace_id=trace_id,
        error=error_message,
        metadata=metadata,
    )

    return failure_event, trace_record.model_dump()
