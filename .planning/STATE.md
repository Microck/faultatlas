# FaultAtlas - Project State

## Current Position

Phase: 4 of 4 (Demo & Submit)
Plan: 4 of 5
Status: In progress
Last activity: 2026-02-11 - Completed 04-04-PLAN.md
Progress: █████████████░ 13/14 plans (93%)

---

## Phase Status

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 1 | Foundation | Complete | 3/3 plans |
| 2 | Analysis Pipeline | Complete | 3/3 plans |
| 3 | Diagnosis & Fixes | Complete | 3/3 plans |
| 4 | Demo & Submit | In progress | 4/5 plans |

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
| 04-02 | DEMO-04 documentation defines exactly 8 counted agents and treats AutopsyController/AutopsyPipeline as orchestration glue | Keeps README and architecture diagram aligned for judge review |
| 04-02 | Mermaid `.mmd` is canonical with README fallback render command for PNG generation | Preserves deliverability when headless Mermaid CLI rendering is unavailable |
| 04-03 | Recording checklist is scenario-anchored and prioritizes live run with explicit mock fallback | Keeps manual video capture repeatable without blocking on Azure/runtime constraints |
| 04-03 | Submission checklist references both `docs/architecture.png` and `docs/architecture.mmd` | Prevents packaging dead-ends when raster diagram export is unavailable |
| 04-01 | Live demo runner calls real modules end-to-end (`run_with_failure_detection` → `AutopsyPipeline` → `DiagnosisEngine` → `FixGenerator`) | Demonstrates actual pipeline behavior for video capture instead of synthetic helper wrappers |
| 04-01 | Mock mode is fixture-backed via `demo/sample_output.md` with the same output sections as live mode | Guarantees reliable no-Azure fallback and keeps narration consistent between modes |
| 04-04 | `docs/architecture.png` is now a committed artifact rendered from `docs/architecture.mmd` | Closes DEMO-04 delivery gap with a review-ready architecture image for submission |
| 04-04 | Human checkpoint approval is required for visual artifact legibility before marking diagram work done | Ensures judge-facing readability is validated beyond file-level checks |

---

## Blockers/Concerns Carried Forward

- Live Cosmos verification still requires user-provided `COSMOS_ENDPOINT`, `COSMOS_KEY`, `COSMOS_DATABASE`, `COSMOS_CONTAINER_TRACES`, and `COSMOS_CONTAINER_FIXES`.
- System Python in this environment lacks required runtime modules; use `.venv/bin/python -m ...` for deterministic plan verification.
- Final manual submission steps remain outside automation: record `demo/video.mp4`, complete `demo/submission_checklist.md`, and submit on the hackathon portal.

---

## Recent Activity

| Date | Activity |
|------|----------|
| 2026-02-11 | Completed Phase 4 Plan 04 execution, verified prior render commit, and closed the architecture PNG submission gap with approved human readability check |
| 2026-02-11 | Completed Phase 4 Plan 03 execution and finalized recording/submission checklists for final packaging |
| 2026-02-11 | Completed Phase 4 Plan 01 execution, added a 2-minute demo script, live/mock demo runner, and sample output fallback |
| 2026-02-11 | Completed Phase 4 Plan 02 execution, added README/demo quickstart docs, failure taxonomy, and architecture Mermaid source |
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

Last session: 2026-02-11T20:40:34Z
Stopped at: Completed 04-04 architecture diagram render plan
Resume file: .planning/phases/04-demo-submit/04-04-SUMMARY.md

---

*Last updated: 2026-02-11*
