from __future__ import annotations

import sys

from opentelemetry import trace

from src.core.foundry_client import load_foundry_config
from src.core.tracing import configure_tracing


def main() -> int:
    cfg = load_foundry_config()
    if not cfg.project_endpoint or not cfg.model_deployment:
        print("Missing Foundry config.")
        print("Set env vars in your shell (or a local .env file):")
        print("  - FOUNDRY_PROJECT_ENDPOINT")
        print("  - FOUNDRY_MODEL_DEPLOYMENT")
        print("(Aliases: AZURE_AI_PROJECT_ENDPOINT / AZURE_AI_MODEL_DEPLOYMENT_NAME)")
        return 2

    exporter = configure_tracing()
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("verify-foundry") as span:
        span.set_attribute("foundry.project_endpoint", cfg.project_endpoint)
        span.set_attribute("foundry.model_deployment", cfg.model_deployment)
        span.set_attribute("tracing.exporter", exporter)

    print(f"Foundry endpoint: {cfg.project_endpoint}")
    print(f"Model deployment: {cfg.model_deployment}")
    print(f"Tracing exporter: {exporter}")

    # Live check requires auth + network.
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential

        with (
            DefaultAzureCredential() as credential,
            AIProjectClient(endpoint=cfg.project_endpoint, credential=credential) as project_client,
        ):
            deployment = project_client.deployments.get(cfg.model_deployment)
            # Keep output minimal; avoid printing full objects.
            name = getattr(deployment, "name", None) or cfg.model_deployment
            print(f"OK: deployment reachable: {name}")
    except Exception as exc:
        print("NOTE: Live Foundry verification did not complete.")
        print(
            "This is expected until you authenticate (e.g. `az login`) and have access to the project."
        )
        print(f"Error: {type(exc).__name__}: {exc}")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
