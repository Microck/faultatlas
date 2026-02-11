from __future__ import annotations

from typing import Any, Protocol

from src.core.autopsy_controller import AutopsyController
from src.models.findings import FindingsReport
from src.storage.trace_store import StoreBackend, TraceStore


class TraceStoreLike(Protocol):
    def get_trace(self, failure_id: str) -> dict[str, Any]: ...


class AutopsyPipeline:
    def __init__(
        self,
        trace_store: TraceStoreLike,
        controller: AutopsyController | None = None,
    ) -> None:
        self._trace_store = trace_store
        self._controller = controller or AutopsyController()

    def run(self, failure_id: str) -> FindingsReport:
        stored_trace = self._trace_store.get_trace(failure_id)
        trace_record = stored_trace.get("trace_record")
        if not isinstance(trace_record, dict):
            raise ValueError(
                "TraceStore.get_trace must return a payload with a dictionary 'trace_record'."
            )

        return self._controller.run_autopsy(trace_record)


def create_trace_store(backend: StoreBackend = "auto") -> TraceStore:
    return TraceStore(backend=backend)


def create_autopsy_pipeline(
    backend: StoreBackend = "auto",
    trace_store: TraceStoreLike | None = None,
    controller: AutopsyController | None = None,
) -> AutopsyPipeline:
    selected_trace_store = trace_store or create_trace_store(backend=backend)
    return AutopsyPipeline(trace_store=selected_trace_store, controller=controller)


def run_autopsy_for_failure(
    failure_id: str,
    backend: StoreBackend = "auto",
    trace_store: TraceStoreLike | None = None,
    controller: AutopsyController | None = None,
) -> FindingsReport:
    pipeline = create_autopsy_pipeline(
        backend=backend,
        trace_store=trace_store,
        controller=controller,
    )
    return pipeline.run(failure_id)
