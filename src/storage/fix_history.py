from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from pydantic import BaseModel

from src.models.diagnosis import Diagnosis
from src.models.findings import FindingsReport
from src.models.fixes import FixProposal
from src.storage.fix_history_memory import InMemoryFixHistory


StoreBackend = Literal["auto", "memory", "cosmos"]


@dataclass(frozen=True)
class FixHistoryCosmosSettings:
    endpoint: str
    key: str
    database: str
    container_fixes: str


def load_fix_history_settings_from_env() -> FixHistoryCosmosSettings | None:
    endpoint = os.getenv("COSMOS_ENDPOINT", "").strip()
    key = os.getenv("COSMOS_KEY", "").strip()
    database = os.getenv("COSMOS_DATABASE", "").strip()
    container_fixes = os.getenv("COSMOS_CONTAINER_FIXES", "").strip()

    if not all((endpoint, key, database, container_fixes)):
        return None

    return FixHistoryCosmosSettings(
        endpoint=endpoint,
        key=key,
        database=database,
        container_fixes=container_fixes,
    )


class FixHistoryLookup(Protocol):
    def find_similar(
        self,
        diagnosis: Diagnosis | dict[str, Any],
        findings_report: FindingsReport | dict[str, Any],
        *,
        limit: int = 5,
    ) -> list[str]: ...


class _FixHistoryBackend(FixHistoryLookup, Protocol):
    def record_failure(
        self,
        failure_event: BaseModel | dict[str, Any],
        diagnosis: Diagnosis | dict[str, Any],
    ) -> None: ...

    def record_fix(
        self,
        failure_id: str,
        fix_proposals: list[FixProposal | dict[str, Any]],
    ) -> None: ...


def _coerce_payload(value: BaseModel | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return dict(value)

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


class _CosmosFixHistoryBackend:
    def __init__(self, settings: FixHistoryCosmosSettings) -> None:
        self._settings = settings
        self._client = CosmosClient(url=settings.endpoint, credential=settings.key)
        database_client = self._client.create_database_if_not_exists(id=settings.database)
        self._container_client = database_client.create_container_if_not_exists(
            id=settings.container_fixes,
            partition_key=PartitionKey(path="/failure_id"),
        )

    @classmethod
    def from_env(cls) -> _CosmosFixHistoryBackend:
        settings = load_fix_history_settings_from_env()
        if settings is None:
            raise ValueError(
                "Missing FixHistory Cosmos configuration. Set COSMOS_ENDPOINT, COSMOS_KEY, "
                "COSMOS_DATABASE, and COSMOS_CONTAINER_FIXES."
            )

        return cls(settings)

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

        existing_fix_proposals: list[dict[str, Any]] = []
        try:
            existing_document = self._container_client.read_item(
                item=failure_id,
                partition_key=failure_id,
            )
            existing_fix_proposals = list(existing_document.get("fix_proposals", []))
        except exceptions.CosmosResourceNotFoundError:
            existing_fix_proposals = []

        document = {
            "id": failure_id,
            "failure_id": failure_id,
            "failure_event": failure_event_payload,
            "diagnosis": diagnosis_payload,
            "root_cause": diagnosis_payload["root_cause"],
            "sub_type": diagnosis_payload.get("sub_type"),
            "fix_proposals": existing_fix_proposals,
        }
        self._container_client.upsert_item(document)

    def record_fix(
        self,
        failure_id: str,
        fix_proposals: list[FixProposal | dict[str, Any]],
    ) -> None:
        normalized_failure_id = str(failure_id).strip()
        if not normalized_failure_id:
            raise ValueError("failure_id is required.")

        try:
            document = self._container_client.read_item(
                item=normalized_failure_id,
                partition_key=normalized_failure_id,
            )
        except exceptions.CosmosResourceNotFoundError as exc:
            raise KeyError(f"Fix history '{normalized_failure_id}' not found.") from exc

        document["fix_proposals"] = _coerce_fix_proposals(fix_proposals)
        self._container_client.upsert_item(document)

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

        query = "SELECT c.failure_id, c.sub_type FROM c WHERE c.root_cause = @root_cause"
        parameters = [{"name": "@root_cause", "value": target_root_cause}]

        similar_failure_ids: list[str] = []
        results = self._container_client.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )

        for row in results:
            if row.get("sub_type") != target_sub_type:
                continue

            failure_id = str(row.get("failure_id", "")).strip()
            if not failure_id:
                continue

            similar_failure_ids.append(failure_id)
            if len(similar_failure_ids) >= limit:
                break

        return similar_failure_ids


class FixHistory(FixHistoryLookup):
    def __init__(self, backend: StoreBackend = "auto") -> None:
        backend_name = backend
        if backend == "auto":
            backend_name = "cosmos" if load_fix_history_settings_from_env() else "memory"

        if backend_name == "memory":
            self._backend: _FixHistoryBackend = InMemoryFixHistory()
            self.backend_name = "memory"
            return

        if backend_name == "cosmos":
            self._backend = _CosmosFixHistoryBackend.from_env()
            self.backend_name = "cosmos"
            return

        raise ValueError(f"Unsupported backend '{backend}'.")

    def record_failure(
        self,
        failure_event: BaseModel | dict[str, Any],
        diagnosis: Diagnosis | dict[str, Any],
    ) -> None:
        self._backend.record_failure(failure_event, diagnosis)

    def record_fix(
        self,
        failure_id: str,
        fix_proposals: list[FixProposal | dict[str, Any]],
    ) -> None:
        self._backend.record_fix(failure_id, fix_proposals)

    def find_similar(
        self,
        diagnosis: Diagnosis | dict[str, Any],
        findings_report: FindingsReport | dict[str, Any],
        *,
        limit: int = 5,
    ) -> list[str]:
        return self._backend.find_similar(diagnosis, findings_report, limit=limit)
