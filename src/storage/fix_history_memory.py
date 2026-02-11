from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import BaseModel

from src.models.diagnosis import Diagnosis
from src.models.findings import FindingsReport
from src.models.fixes import FixProposal


def _coerce_payload(value: BaseModel | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return deepcopy(value)

    raise TypeError("FixHistory payloads must be dicts or pydantic models.")


def _coerce_fix_proposals(
    fix_proposals: list[FixProposal | dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for fix_proposal in fix_proposals:
        if isinstance(fix_proposal, dict):
            normalized.append(FixProposal.model_validate(fix_proposal).model_dump(mode="json"))
            continue
        normalized.append(FixProposal.model_validate(fix_proposal).model_dump(mode="json"))

    return normalized


class InMemoryFixHistory:
    def __init__(self) -> None:
        self._documents: dict[str, dict[str, Any]] = {}

    def record_failure(
        self,
        failure_event: BaseModel | dict[str, Any],
        diagnosis: Diagnosis | dict[str, Any],
    ) -> None:
        failure_event_payload = _coerce_payload(failure_event)
        diagnosis_payload = Diagnosis.model_validate(diagnosis).model_dump(mode="json")

        failure_id = str(failure_event_payload.get("failure_id", "")).strip()
        if not failure_id:
            raise ValueError("failure_event is missing 'failure_id'.")

        existing = self._documents.get(failure_id, {})
        self._documents[failure_id] = {
            "id": failure_id,
            "failure_id": failure_id,
            "failure_event": failure_event_payload,
            "diagnosis": diagnosis_payload,
            "root_cause": diagnosis_payload["root_cause"],
            "sub_type": diagnosis_payload.get("sub_type"),
            "fix_proposals": deepcopy(existing.get("fix_proposals", [])),
        }

    def record_fix(
        self,
        failure_id: str,
        fix_proposals: list[FixProposal | dict[str, Any]],
    ) -> None:
        normalized_failure_id = str(failure_id).strip()
        if not normalized_failure_id:
            raise ValueError("failure_id is required.")
        if normalized_failure_id not in self._documents:
            raise KeyError(f"Fix history '{normalized_failure_id}' not found.")

        self._documents[normalized_failure_id]["fix_proposals"] = _coerce_fix_proposals(
            fix_proposals
        )

    def find_similar(
        self,
        diagnosis: Diagnosis | dict[str, Any],
        findings_report: FindingsReport | dict[str, Any],
        *,
        limit: int = 5,
    ) -> list[str]:
        if limit <= 0:
            return []

        diagnosis_payload = Diagnosis.model_validate(diagnosis).model_dump(mode="json")
        FindingsReport.model_validate(findings_report)

        target_root_cause = str(diagnosis_payload["root_cause"])
        target_sub_type = diagnosis_payload.get("sub_type")

        similar_failure_ids: list[str] = []
        for failure_id, document in self._documents.items():
            if document.get("root_cause") != target_root_cause:
                continue
            if document.get("sub_type") != target_sub_type:
                continue

            similar_failure_ids.append(failure_id)
            if len(similar_failure_ids) >= limit:
                break

        return similar_failure_ids
