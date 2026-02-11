from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


FailureType = Literal[
    "exception",
    "validation_error",
    "timeout",
    "hallucination_flag",
    "none",
]


class FailureEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    failure_id: str
    subject: str
    failure_type: FailureType
    timestamp: str
    trace_id: str | None = None
    error: str
    metadata: dict[str, Any] = Field(default_factory=dict)
