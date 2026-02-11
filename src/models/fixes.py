from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class FixType(str, Enum):
    PROMPT_FIX = "PROMPT_FIX"
    TOOL_CONFIG_FIX = "TOOL_CONFIG_FIX"
    GUARDRAIL_FIX = "GUARDRAIL_FIX"


class FixChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file: str
    change_type: str
    before: str
    after: str
    diff: str


class FixProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fix_type: FixType
    title: str
    rationale: str
    changes: list[FixChange] = Field(default_factory=list)
