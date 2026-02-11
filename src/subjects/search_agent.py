from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.tools.registry import ToolRegistry


def search_scenario_payload() -> dict[str, Any]:
    return {
        "input": {
            "instruction": "Find something useful and summarize it quickly.",
            "ambiguity": "No concrete source material provided.",
        },
        "tool_calls": [
            {
                "tool": "summarize_sources",
                "args": {"sources": []},
            }
        ],
    }


def run_search_scenario(registry: ToolRegistry | None = None) -> dict[str, Any]:
    payload = search_scenario_payload()
    active_registry = registry or ToolRegistry()

    active_registry.validate_payload(payload["tool_calls"][0])

    result = {"subject": "search", "status": "passed"}
    result.update(deepcopy(payload))
    return result
