from __future__ import annotations

import os
from typing import Literal


_configured = False


ExporterType = Literal["azure-monitor", "console"]


def configure_tracing() -> ExporterType:
    """Configure OpenTelemetry tracing.

    - If APPLICATIONINSIGHTS_CONNECTION_STRING is set, use Azure Monitor exporter.
    - Otherwise, fall back to console exporter so local dev still shows spans.
    """

    global _configured
    if _configured:
        # Best-effort: avoid reconfiguring global providers.
        return "azure-monitor" if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING") else "console"

    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if connection_string:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=connection_string)
        _configured = True
        return "azure-monitor"

    # Console fallback
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
    from opentelemetry import trace

    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    _configured = True
    return "console"
