from __future__ import annotations

from pathlib import Path
from typing import Any

from src.tools.schema_registry import SchemaRegistry


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
        try:
            self._schema_registry = SchemaRegistry(schemas_dir=schemas_dir)
        except ValueError as error:
            raise ToolValidationError(
                "registry",
                str(error),
                code="schema_load_error",
            ) from error

    @property
    def available_tools(self) -> tuple[str, ...]:
        return self._schema_registry.list_tools()

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
        mismatches = self._schema_registry.validate(tool_name, args)
        if mismatches:
            first_mismatch = mismatches[0]
            details = dict(first_mismatch.get("details", {}))
            path = first_mismatch.get("path")
            if path is not None:
                details.setdefault("path", path)
            raise ToolValidationError(
                tool_name,
                str(first_mismatch.get("message", "Tool validation failed.")),
                code=str(first_mismatch.get("code", "schema_validation_failed")),
                details=details,
            )

        return {"tool": tool_name, "args": args}
