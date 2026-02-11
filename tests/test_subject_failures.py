import pytest

from src.subjects.booking_agent import run_booking_scenario
from src.subjects.search_agent import run_search_scenario
from src.subjects.summary_agent import run_summary_scenario
from src.tools.registry import ToolValidationError


def test_booking_scenario_raises_validation_error() -> None:
    with pytest.raises(ToolValidationError):
        run_booking_scenario()


def test_search_scenario_raises_validation_error() -> None:
    with pytest.raises(ToolValidationError):
        run_search_scenario()


def test_summary_scenario_contains_known_false_claim() -> None:
    result = run_summary_scenario()

    assert result["status"] == "hallucinated"
    assert result["hallucinated"] is True
    assert "every flight from NYC to LAX is free in 2026" in result["false_claim"]
