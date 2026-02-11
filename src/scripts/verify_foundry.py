from __future__ import annotations

import sys

from opentelemetry import trace

from src.core.foundry_client import create_project_client, load_foundry_config
from src.core.tracing import configure_tracing


def _strict_mode(argv: list[str]) -> bool:
    return "--strict" in argv


def main() -> int:
    strict = _strict_mode(sys.argv[1:])
    cfg = load_foundry_config()
    print(f"Foundry endpoint: {cfg.project_endpoint or '<missing>'}")
    print(f"Model deployment: {cfg.model_deployment or '<missing>'}")

    exporter = configure_tracing()
    print(f"Tracing exporter: {exporter}")

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("verify-foundry") as span:
        span.set_attribute("foundry.project_endpoint", cfg.project_endpoint or "")
        span.set_attribute("foundry.model_deployment", cfg.model_deployment or "")
        span.set_attribute("tracing.exporter", exporter)

    if not cfg.project_endpoint or not cfg.model_deployment:
        print("NOTE: Missing Foundry config.")
        print("Set env vars in your shell (or a local .env file):")
        print("  - FOUNDRY_PROJECT_ENDPOINT")
        print("  - FOUNDRY_MODEL_DEPLOYMENT")
        print("Tip: pass --strict to fail this command when configuration is missing.")
        return 2 if strict else 0

    # Live check requires auth + network.
    try:
        with create_project_client(cfg) as project_client:
            deployment = project_client.deployments.get(cfg.model_deployment)
            name = getattr(deployment, "name", None) or cfg.model_deployment
            print(f"OK: deployment reachable: {name}")
    except Exception as exc:
        print("NOTE: Live Foundry verification did not complete.")
        print(
            "This is expected until you authenticate (e.g. `az login`) and have access to the project."
        )
        print(f"Error: {type(exc).__name__}: {exc}")
        print("Tip: pass --strict to fail this command when live validation is unavailable.")
        return 3 if strict else 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
