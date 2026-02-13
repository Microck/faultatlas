from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from typing import cast


SUBJECT_CHOICES = ("booking", "search", "summary")
STORE_CHOICES = ("memory", "cosmos")
SAMPLE_OUTPUT_PATH = Path(__file__).with_name("sample_output.md")
REPO_ROOT = Path(__file__).resolve().parents[1]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _extract_json_from_markdown(markdown_text: str) -> dict[str, Any]:
    stripped = markdown_text.strip()
    if stripped.startswith("{"):
        return json.loads(stripped)

    fence_start = markdown_text.find("```json")
    if fence_start == -1:
        raise ValueError("sample_output.md must contain a ```json fenced block.")

    json_start = markdown_text.find("\n", fence_start)
    if json_start == -1:
        raise ValueError("Unable to locate JSON block start in sample_output.md.")

    json_start += 1
    json_end = markdown_text.find("```", json_start)
    if json_end == -1:
        raise ValueError("Unable to locate JSON block end in sample_output.md.")

    return json.loads(markdown_text[json_start:json_end].strip())


def _load_mock_output() -> dict[str, Any]:
    return _extract_json_from_markdown(SAMPLE_OUTPUT_PATH.read_text(encoding="utf-8"))


def _extract_scenario_input(trace_record: dict[str, Any]) -> dict[str, Any] | None:
    steps = trace_record.get("steps")
    if not isinstance(steps, list) or not steps:
        return None

    first_step = steps[0]
    if not isinstance(first_step, dict):
        return None

    input_payload = first_step.get("input")
    if isinstance(input_payload, dict):
        return input_payload

    output_payload = first_step.get("output")
    if not isinstance(output_payload, dict):
        return None

    nested_input = output_payload.get("input")
    if isinstance(nested_input, dict):
        return nested_input

    return None


def _run_live(subject: str, store: str, timeout_s: float) -> dict[str, Any]:
    from src.core import diagnosis_engine, fix_generator, indagine_pipeline
    from src.core.failure_detector import run_with_failure_detection
    from src.storage.trace_store import StoreBackend, TraceStore
    from src.subjects.run_subjects import run_subject_scenario

    failure_event, trace_record = run_with_failure_detection(
        subject,
        lambda: run_subject_scenario(subject),
        timeout_s=timeout_s,
    )

    trace_store = TraceStore(backend=cast(StoreBackend, store))
    trace_store.store_trace(failure_event, trace_record)
    stored_trace = trace_store.get_trace(failure_event.failure_id)

    pipeline = indagine_pipeline.IndaginePipeline(trace_store=trace_store)
    findings_report = pipeline.run(failure_event.failure_id)
    diagnosis = diagnosis_engine.DiagnosisEngine().diagnose(findings_report)
    fixes = fix_generator.FixGenerator().generate_fixes(diagnosis, findings_report)

    trace_payload = stored_trace["trace_record"]
    scenario_input = _extract_scenario_input(trace_payload)

    return {
        "mode": "live",
        "subject": subject,
        "store": trace_store.backend_name,
        "scenario_input": scenario_input,
        "failure_event": failure_event.model_dump(mode="json"),
        "findings": findings_report.model_dump(mode="json"),
        "diagnosis": diagnosis.model_dump(mode="json"),
        "fixes": [proposal.model_dump(mode="json") for proposal in fixes],
    }


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Indagine demo in live or fixture-backed mode."
    )
    parser.add_argument("--mode", choices=("mock", "live"), default="mock")
    parser.add_argument("--subject", choices=SUBJECT_CHOICES, default="booking")
    parser.add_argument("--store", choices=STORE_CHOICES, default="memory")
    parser.add_argument("--timeout-s", type=float, default=5.0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.mode == "mock":
        output = _load_mock_output()
    else:
        try:
            output = _run_live(subject=args.subject, store=args.store, timeout_s=args.timeout_s)
        except ModuleNotFoundError as exc:
            missing_module = exc.name or str(exc)
            raise SystemExit(
                "Missing runtime dependency "
                f"'{missing_module}'. Use .venv/bin/python demo/run_demo.py --mode live."
            ) from exc

    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
