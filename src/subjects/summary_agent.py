from __future__ import annotations

from copy import deepcopy
from typing import Any


_FALSE_CLAIM = "The provided sources prove every flight from NYC to LAX is free in 2026."


def summary_scenario_payload() -> dict[str, Any]:
    return {
        "input": {
            "sources": [
                "Source A: NYC to LAX flights operate daily.",
                "Source B: Typical one-way fares are between $120 and $450.",
            ]
        },
        "tool_calls": [
            {
                "tool": "summarize_sources",
                "args": {
                    "sources": [
                        "Source A: NYC to LAX flights operate daily.",
                        "Source B: Typical one-way fares are between $120 and $450.",
                    ]
                },
            }
        ],
    }


def run_summary_scenario() -> dict[str, Any]:
    payload = summary_scenario_payload()
    result = {
        "subject": "summary",
        "status": "hallucinated",
        "hallucinated": True,
        "summary": (
            "The sources mention regular routes and ordinary fares, and they also confirm a special "
            "promotion where every seat is free."
        ),
        "false_claim": _FALSE_CLAIM,
    }
    result.update(deepcopy(payload))
    return result
