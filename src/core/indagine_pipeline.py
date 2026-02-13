from __future__ import annotations

from typing import Any, Protocol

from src.core.indagine_controller import IndagineController
from src.models.findings import FindingsReport
from src.storage.trace_store import StoreBackend, TraceStore


class TraceStoreLike(Protocol):
    def get_trace(self, failure_id: str) -> dict[str, Any]: ...


class IndaginePipeline:
    def __init__(
        self,
        trace_store: TraceStoreLike,
        controller: IndagineController | None = None,
    ) -> None:
        self._trace_store = trace_store
        self._controller = controller or IndagineController()

    def run(self, failure_id: str) -> FindingsReport:
        stored_trace = self._trace_store.get_trace(failure_id)
        trace_record = stored_trace.get("trace_record")
        if not isinstance(trace_record, dict):
            raise ValueError(
                "TraceStore.get_trace must return a payload with a dictionary 'trace_record'."
            )

        return self._controller.run_indagine(trace_record)


def create_trace_store(backend: StoreBackend = "auto") -> TraceStore:
    return TraceStore(backend=backend)


def create_indagine_pipeline(
    backend: StoreBackend = "auto",
    trace_store: TraceStoreLike | None = None,
    controller: IndagineController | None = None,
) -> IndaginePipeline:
    selected_trace_store = trace_store or create_trace_store(backend=backend)
    return IndaginePipeline(trace_store=selected_trace_store, controller=controller)


def run_indagine_for_failure(
    failure_id: str,
    backend: StoreBackend = "auto",
    trace_store: TraceStoreLike | None = None,
    controller: IndagineController | None = None,
) -> FindingsReport:
    pipeline = create_indagine_pipeline(
        backend=backend,
        trace_store=trace_store,
        controller=controller,
    )
    return pipeline.run(failure_id)
