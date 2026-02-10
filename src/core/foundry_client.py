from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

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


def load_foundry_config() -> FoundryConfig:
    """Load Foundry config from env first, then infra YAML.

    Supported env var aliases:
    - endpoint: FOUNDRY_PROJECT_ENDPOINT or AZURE_AI_PROJECT_ENDPOINT
    - deployment: FOUNDRY_MODEL_DEPLOYMENT or AZURE_AI_MODEL_DEPLOYMENT_NAME
    """

    # Load optional local .env file (ignored by git).
    load_dotenv(override=False)

    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT") or os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    deployment = os.getenv("FOUNDRY_MODEL_DEPLOYMENT") or os.getenv(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME"
    )

    if endpoint and deployment:
        return FoundryConfig(project_endpoint=endpoint.strip(), model_deployment=deployment.strip())

    config_path = _default_config_path()
    if config_path.exists():
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
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
    credential = create_credential()
    return AIProjectClient(endpoint=cfg.project_endpoint, credential=credential)
