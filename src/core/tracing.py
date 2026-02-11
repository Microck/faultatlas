from __future__ import annotations

import os
from typing import Literal

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


_configured = False
_active_exporter: "ExporterType | None" = None


ExporterType = Literal["azure-monitor", "console"]


def _connection_string_from_env() -> str | None:
    value = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "").strip()
    return value or None


def _connection_string_from_foundry() -> str | None:
    """Best-effort lookup from Foundry project telemetry."""

    try:
        from src.core.foundry_client import create_project_client, load_foundry_config

        cfg = load_foundry_config()
        if not cfg.project_endpoint:
            return None

        with create_project_client(cfg) as project_client:
            telemetry = getattr(project_client, "telemetry", None)
            if telemetry is None:
                return None

            getter = getattr(telemetry, "get_application_insights_connection_string", None)
            if getter is None:
                return None

            value = getter()
            return value.strip() if isinstance(value, str) and value.strip() else None
    except Exception:
        return None


def configure_tracing() -> ExporterType:
    """Configure OpenTelemetry tracing.

    Preference order:
    1. APPLICATIONINSIGHTS_CONNECTION_STRING env var
    2. Foundry project telemetry connection string
    3. Console exporter fallback for local development
    """

    global _active_exporter, _configured
    if _configured and _active_exporter is not None:
        print(f"Tracing exporter active: {_active_exporter}")
        return _active_exporter

    connection_string = _connection_string_from_env() or _connection_string_from_foundry()
    if connection_string:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=connection_string)
        _active_exporter = "azure-monitor"
        _configured = True
        print("Tracing exporter active: azure-monitor")
        return "azure-monitor"

    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    _active_exporter = "console"
    _configured = True
    print("Tracing exporter active: console")
    return "console"
