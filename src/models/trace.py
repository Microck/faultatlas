from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_rfc3339(value: str) -> str:
    candidate = value
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"

    try:
        datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(f"Invalid RFC3339 timestamp: {value}") from exc

    return value


class TraceToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str
    args: dict[str, Any] = Field(default_factory=dict)


class TraceStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    kind: str
    timestamp: str | None = None
    input: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    tool_calls: list[TraceToolCall] = Field(default_factory=list)
    thought: str | None = None
    decision: str | None = None
    error: str | None = None

    @field_validator("timestamp")
    @classmethod
    def _timestamp_must_be_rfc3339(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validate_rfc3339(value)


class TraceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    failure_id: str
    subject: str
    status: Literal["failed", "hallucinated", "passed"]
    started_at: str
    ended_at: str
    steps: list[TraceStep] = Field(default_factory=list)

    @field_validator("started_at", "ended_at")
    @classmethod
    def _timestamps_must_be_rfc3339(cls, value: str) -> str:
        return _validate_rfc3339(value)
