# FaultAtlas - Project State

## Current Position

Phase: 3 of 4 (Diagnosis & Fixes)
Plan: 3 of 3
Status: Phase complete
Last activity: 2026-02-11 - Approved Phase 3 verification checkpoint (live Cosmos checks deferred)
Progress: █████████░░░ 9/12 plans (75%)

---

## Phase Status

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 1 | Foundation | Complete | 3/3 plans |
| 2 | Analysis Pipeline | Complete | 3/3 plans |
| 3 | Diagnosis & Fixes | Complete | 3/3 plans |
| 4 | Demo & Submit | Not Started | 0/3 plans |

---

## Phase 1 Requirement Snapshot

| REQ-ID | Requirement | Status | Notes |
|--------|-------------|--------|-------|
| FOUND-01 | Foundry project initialized with tracing enabled | Completed | Strict verification path implemented and approved |
| FOUND-02 | BookingAgent that can fail on date format parsing | Completed | Deterministic DD/MM/YYYY schema-validation failure added with CLI + tests |
| FOUND-03 | SearchAgent that can fail on wrong tool selection | Completed | Ambiguous instruction now deterministically fails tool validation |
| FOUND-04 | SummaryAgent that can hallucinate information | Completed | Reproducible hallucinated output with explicit false claim marker |
| FOUND-05 | Failure Detector that watches for exceptions, validation failures, timeouts | Completed | Structured FailureEvent + TraceRecord emitted for booking/search/summary scenarios |
| FOUND-06 | Trace capture stores execution traces to Cosmos DB | Completed | Implementation approved; live Cosmos verification remains pending credentials |

---

## Decisions

| Phase | Decision | Rationale |
|-------|----------|-----------|
| 01-01 | Canonicalized direct runtime config to `FOUNDRY_PROJECT_ENDPOINT` + `FOUNDRY_MODEL_DEPLOYMENT` with YAML fallback | Keeps a single predictable env surface and avoids alias drift |
| 01-01 | Added `--strict` mode to `verify_foundry` while keeping default local-friendly behavior | Enables deterministic local scaffolding checks without blocking strict CI/live validation |
| 01-02 | Subject scenario functions fail deterministically via shared `ToolValidationError` contract | Keeps failure assertions stable for tests and future analyzers |
| 01-02 | Runner reports `failed`/`hallucinated` in JSON while always exiting 0 | Allows deterministic batch execution without shell-level flakiness |
| 01-03 | Pinned `TraceRecord` contract to `schema_version=1` with `extra="forbid"` | Prevents silent schema drift before analyzers depend on trace payload shape |
| 01-03 | Defaulted TraceStore to memory fallback and keyed persistence by `failure_id` | Keeps local end-to-end runs unblocked while preserving direct retrieval semantics |
| 02-01 | Failure step indexing is 1-based (`step N of M`) in TraceAnalyzer output | Matches requirement language and keeps analyzer output unambiguous |
| 02-01 | Reasoning chain extraction prioritizes `thought`/`decision` then deterministic fallback from trace artifacts | Preserves explicit model reasoning when present while guaranteeing stable output for Phase 1 traces |
| 02-02 | SchemaRegistry became the shared schema source while ToolRegistry stayed as a compatibility wrapper | Enables analyzer reuse without breaking subject scenario validation behavior |
| 02-02 | Wrong-tool detection now checks `metadata.intended_tool` first, then falls back to search-intent heuristic | Makes SearchAgent TOOL_MISUSE diagnosable even when trace metadata is incomplete |
| 02-03 | Autopsy findings are keyed as `trace_analyzer` and `tool_analyzer` in a unified `FindingsReport` envelope | Creates a stable analyzer contract for Phase 3 diagnosis consumers |
| 02-03 | AutopsyPipeline uses injected TraceStore and delegates backend/env selection to TraceStore helpers | Keeps pipeline glue Azure-agnostic and avoids duplicate backend configuration parsing |
| 03-01 | `Diagnosis.similar_past_failures` is derived from `similar_past_failure_ids` via computed field | Guarantees DIAG-04 count consistency without manual sync drift |
| 03-01 | Diagnosis classification priority is deterministic by marker strength (tool misuse > hallucination > prompt ambiguity > context overflow > coordination > fallback) | Keeps root-cause outputs stable and explainable for fixture-driven verification |
| 03-02 | FixGenerator maps each taxonomy root cause to deterministic fix templates with explicit target files | Guarantees FIX-01..FIX-03 proposal availability for every diagnosis type |
| 03-02 | Fix proposal diffs use stdlib unified format (`---`/`+++`) generated from exact before/after snippets | Satisfies FIX-04 reviewability and keeps change artifacts auditable |
| 03-03 | FixHistory now uses auto backend selection (Cosmos when all fix-history env vars exist, otherwise memory) | Keeps local development unblocked while enabling Cosmos-backed similarity history in configured environments |
| 03-03 | DiagnosisEngine now resolves DIAG-04 links through `FixHistory.find_similar(...)` rather than payload introspection | Makes similarity linking explicit, testable, and backend-driven |

---

## Blockers/Concerns Carried Forward

- Live Cosmos verification still requires user-provided `COSMOS_ENDPOINT`, `COSMOS_KEY`, `COSMOS_DATABASE`, `COSMOS_CONTAINER_TRACES`, and `COSMOS_CONTAINER_FIXES`.
- System Python in this environment lacks required runtime modules; use `.venv/bin/python -m ...` for deterministic plan verification.

---

## Recent Activity

| Date | Activity |
|------|----------|
| 2026-02-11 | User approved Phase 3 verification checkpoint; phase marked complete with live Cosmos similarity checks pending credentials |
| 2026-02-11 | Completed Phase 3 Plan 03 execution, added fix-history storage backends, similarity lookup tests, and DiagnosisEngine DIAG-04 wiring |
| 2026-02-11 | Completed Phase 3 Plan 02 execution, added fix proposal models, unified diff utilities, taxonomy-wide FixGenerator coverage, and tests |
| 2026-02-11 | Completed Phase 3 Plan 01 execution, added Diagnosis model/taxonomy, deterministic DiagnosisEngine, and taxonomy-coverage tests |
| 2026-02-11 | Completed Phase 2 Plan 03 execution, added AutopsyController orchestration, pipeline wiring, and integration contract tests |
| 2026-02-11 | Completed Phase 2 Plan 02 execution, added shared SchemaRegistry and ToolAnalyzer with fixture-driven misuse checks |
| 2026-02-11 | Completed Phase 2 Plan 01 execution, added trace/findings models and TraceAnalyzer with fixture-driven tests |
| 2026-02-11 | User approved Phase 1 verification checkpoint; phase marked complete with Cosmos live-check pending |
| 2026-02-11 | Completed Phase 1 Plan 03 execution, added failure detection + trace persistence, and updated state |
| 2026-02-11 | Completed Phase 1 Plan 02 execution, created deterministic subject scenarios, updated state |
| 2026-02-11 | Completed Phase 1 Plan 01 execution, created summary, updated state |
| 2026-02-08 | Project initialized, requirements defined, roadmap created |

---

## Session Continuity

Last session: 2026-02-11T04:42:05Z
Stopped at: Phase 3 verification approved (human-needed Cosmos checks deferred)
Resume file: .planning/phases/04-demo-submit/04-01-PLAN.md

---

*Last updated: 2026-02-11*
