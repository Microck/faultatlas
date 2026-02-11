from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class FoundryConfig:
    project_endpoint: str
    model_deployment: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_config_path() -> Path:
    return _repo_root() / "infra" / "foundry_config.yaml"


def _read_yaml_defaults(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def load_foundry_config() -> FoundryConfig:
    """Load Foundry config from env first, then infra YAML."""

    # Load optional local .env file (ignored by git).
    load_dotenv(override=False)

    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    deployment = os.getenv("FOUNDRY_MODEL_DEPLOYMENT")

    if endpoint and deployment:
        return FoundryConfig(project_endpoint=endpoint.strip(), model_deployment=deployment.strip())

    data = _read_yaml_defaults(_default_config_path())
    endpoint = endpoint or str(data.get("project_endpoint") or "")
    deployment = deployment or str(data.get("model_deployment") or "")

    return FoundryConfig(
        project_endpoint=(endpoint or "").strip(), model_deployment=(deployment or "").strip()
    )


def create_credential():
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential()


def create_project_client(config: FoundryConfig | None = None):
    """Create an Azure AI Projects client for the configured Foundry project."""

    from azure.ai.projects import AIProjectClient

    cfg = config or load_foundry_config()
    if not cfg.project_endpoint:
        raise ValueError(
            "Missing Foundry project endpoint. Set FOUNDRY_PROJECT_ENDPOINT or infra/foundry_config.yaml."
        )

    credential = create_credential()
    return AIProjectClient(endpoint=cfg.project_endpoint, credential=credential)
