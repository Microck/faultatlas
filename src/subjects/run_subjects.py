from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from src.subjects.booking_agent import booking_scenario_payload, run_booking_scenario
from src.subjects.search_agent import run_search_scenario, search_scenario_payload
from src.subjects.summary_agent import run_summary_scenario
from src.tools.registry import ToolValidationError


_VALID_STATUSES = {"passed", "failed", "hallucinated"}


def _validation_failure(
    subject: str, payload: dict[str, Any], error: ToolValidationError
) -> dict[str, Any]:
    return {
        "subject": subject,
        "status": "failed",
        "input": payload["input"],
        "tool_calls": payload["tool_calls"],
        "error": error.to_dict(),
    }


def run_subject_scenario(subject: str) -> dict[str, Any]:
    if subject == "booking":
        payload = booking_scenario_payload()
        try:
            return run_booking_scenario()
        except ToolValidationError as error:
            return _validation_failure(subject, payload, error)

    if subject == "search":
        payload = search_scenario_payload()
        try:
            return run_search_scenario()
        except ToolValidationError as error:
            return _validation_failure(subject, payload, error)

    if subject == "summary":
        return run_summary_scenario()

    raise ValueError(f"Unsupported subject '{subject}'.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic subject scenarios.")
    parser.add_argument("subject", choices=["booking", "search", "summary"])
    args = parser.parse_args(argv)

    result = run_subject_scenario(args.subject)
    status = result.get("status")
    if status not in _VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'.")

    json.dump(result, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
