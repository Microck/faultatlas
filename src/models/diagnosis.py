from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field


class FailureTaxonomy(str, Enum):
    PROMPT_AMBIGUITY = "PROMPT_AMBIGUITY"
    TOOL_MISUSE = "TOOL_MISUSE"
    HALLUCINATION = "HALLUCINATION"
    CONTEXT_OVERFLOW = "CONTEXT_OVERFLOW"
    REASONING_ERROR = "REASONING_ERROR"
    COORDINATION_FAILURE = "COORDINATION_FAILURE"


class Diagnosis(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    root_cause: FailureTaxonomy
    sub_type: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    affected_subjects: list[str] = Field(default_factory=list)
    similar_past_failure_ids: list[str] = Field(default_factory=list)

    @computed_field(return_type=int)
    @property
    def similar_past_failures(self) -> int:
        return len(self.similar_past_failure_ids)
