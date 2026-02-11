from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.tools.registry import ToolRegistry


def booking_scenario_payload() -> dict[str, Any]:
    return {
        "input": {
            "request": "Book a flight from NYC to LAX on 15/02/2026",
            "date": "15/02/2026",
            "from": "NYC",
            "to": "LAX",
        },
        "tool_calls": [
            {
                "tool": "search_flights",
                "args": {
                    "date": "15/02/2026",
                    "from": "NYC",
                    "to": "LAX",
                },
            }
        ],
    }


def run_booking_scenario(registry: ToolRegistry | None = None) -> dict[str, Any]:
    payload = booking_scenario_payload()
    active_registry = registry or ToolRegistry()

    active_registry.validate_payload(payload["tool_calls"][0])

    result = {"subject": "booking", "status": "passed"}
    result.update(deepcopy(payload))
    return result
