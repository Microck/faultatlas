from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


SchemaMismatch = dict[str, Any]


class SchemaRegistry:
    def __init__(self, schemas_dir: Path | None = None) -> None:
        self._schemas_dir = schemas_dir or Path(__file__).resolve().parent / "schemas"
        self._schemas, self._validators = self._load_schemas()

    def _load_schemas(self) -> tuple[dict[str, dict[str, Any]], dict[str, Draft202012Validator]]:
        schemas: dict[str, dict[str, Any]] = {}
        validators: dict[str, Draft202012Validator] = {}

        for schema_path in sorted(self._schemas_dir.glob("*.json")):
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            tool_name = schema_path.stem
            schemas[tool_name] = schema
            validators[tool_name] = Draft202012Validator(schema)

        if not validators:
            raise ValueError(f"No tool schemas found in {self._schemas_dir}")

        return schemas, validators

    def list_tools(self) -> tuple[str, ...]:
        return tuple(sorted(self._validators))

    def get_schema(self, tool_name: str) -> dict[str, Any]:
        schema = self._schemas.get(tool_name)
        if schema is None:
            raise KeyError(f"Unknown tool '{tool_name}'.")
        return json.loads(json.dumps(schema))

    def validate(self, tool_name: str, args: dict[str, Any]) -> list[SchemaMismatch]:
        validator = self._validators.get(tool_name)
        if validator is None:
            return [
                {
                    "code": "unknown_tool",
                    "message": f"Unknown tool '{tool_name}'.",
                    "details": {"available_tools": list(self.list_tools())},
                }
            ]

        if not isinstance(args, dict):
            return [
                {
                    "code": "invalid_payload",
                    "message": "Tool args must be an object.",
                    "path": "<root>",
                }
            ]

        errors = sorted(
            validator.iter_errors(args),
            key=lambda err: tuple(str(piece) for piece in err.absolute_path),
        )
        mismatches: list[SchemaMismatch] = []
        for error in errors:
            path = ".".join(str(piece) for piece in error.absolute_path) or "<root>"
            mismatches.append(
                {
                    "code": "schema_validation_failed",
                    "message": error.message,
                    "path": path,
                }
            )

        return mismatches
