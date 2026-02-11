from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TraceFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    failure_step: int | None = None
    total_steps: int
    failure_location: str | None = None
    error: str | None = None
    reasoning_chain: list[str] = Field(default_factory=list)


class ToolFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str | None = None
    issue: str | None = None
    expected: dict[str, Any] | None = None
    actual: dict[str, Any] | None = None


class FindingsReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    findings: dict[str, list[TraceFinding | ToolFinding]] = Field(default_factory=dict)
