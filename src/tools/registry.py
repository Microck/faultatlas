from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


class ToolValidationError(Exception):
    def __init__(
        self,
        tool: str,
        message: str,
        *,
        code: str = "validation_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.tool = tool
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(f"{tool}: {message}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class ToolRegistry:
    def __init__(self, schemas_dir: Path | None = None) -> None:
        self._schemas_dir = schemas_dir or Path(__file__).resolve().parent / "schemas"
        self._validators = self._load_validators()

    @property
    def available_tools(self) -> tuple[str, ...]:
        return tuple(sorted(self._validators))

    def _load_validators(self) -> dict[str, Draft202012Validator]:
        validators: dict[str, Draft202012Validator] = {}
        for schema_path in sorted(self._schemas_dir.glob("*.json")):
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            validators[schema_path.stem] = Draft202012Validator(schema)

        if not validators:
            raise ToolValidationError(
                "registry",
                f"No tool schemas found in {self._schemas_dir}",
                code="schema_load_error",
            )

        return validators

    def validate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ToolValidationError(
                "payload",
                "Tool payload must be an object with 'tool' and 'args'.",
                code="invalid_payload",
            )

        tool_name = payload.get("tool")
        args = payload.get("args")
        if not isinstance(tool_name, str) or not tool_name.strip():
            raise ToolValidationError(
                "payload",
                "Tool payload is missing a valid 'tool' field.",
                code="invalid_payload",
            )
        if not isinstance(args, dict):
            raise ToolValidationError(
                tool_name,
                "Tool payload is missing a valid 'args' object.",
                code="invalid_payload",
            )

        return self.validate(tool_name, args)

    def validate(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        validator = self._validators.get(tool_name)
        if validator is None:
            raise ToolValidationError(
                tool_name,
                f"Unknown tool '{tool_name}'.",
                code="unknown_tool",
                details={"available_tools": list(self.available_tools)},
            )

        errors = sorted(
            validator.iter_errors(args),
            key=lambda err: tuple(str(piece) for piece in err.absolute_path),
        )
        if errors:
            first_error = errors[0]
            error_path = ".".join(str(piece) for piece in first_error.absolute_path) or "<root>"
            raise ToolValidationError(
                tool_name,
                first_error.message,
                code="schema_validation_failed",
                details={"path": error_path},
            )

        return {"tool": tool_name, "args": args}
