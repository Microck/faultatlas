---
phase: 04-demo-submit
plan: "01"
subsystem: demo
tags: [python, demo, fixtures, indagine-pipeline]

requires:
  - phase: 03-diagnosis-fixes
    provides: Deterministic diagnosis + fix generation pipeline used for live demo output
provides:
  - Two-minute narrated demo script for the BookingAgent DD/MM/YYYY failure
  - CLI demo runner with live (pipeline) and mock (fixture) execution modes
  - Deterministic fallback sample output for no-Azure recording paths
affects: [04-demo-submit, demo-recording, submission-assets]

tech-stack:
  added: []
  patterns: [dual-mode demo execution, fixture-backed fallback output, lazy cosmos dependency loading]

key-files:
  created:
    - demo/scenario.md
    - demo/run_demo.py
    - demo/sample_output.md
  modified:
    - src/storage/trace_store.py

key-decisions:
  - "Live demo mode executes the real pipeline using run_with_failure_detection -> TraceStore -> IndaginePipeline -> DiagnosisEngine -> FixGenerator."
  - "Mock demo mode reads a fenced JSON fixture from demo/sample_output.md so recording never blocks on Azure availability."

patterns-established:
  - "Demo outputs use one stable shape across live and mock modes: failure_event, findings, diagnosis, fixes."
  - "TraceStore now lazy-loads Cosmos dependencies so memory backend remains usable without Azure SDK modules installed."

duration: 5 min
completed: 2026-02-11
---

# Phase 4 Plan 1: Demo Script and Runner Summary

**Indagine now has a rehearsable 2-minute BookingAgent failure script and a single command runner that emits full failure-to-fix output in either live memory-backed mode or deterministic mock mode.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-11T17:40:08Z
- **Completed:** 2026-02-11T17:45:40Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added `demo/scenario.md` with a timestamped 0:00-2:00 narration, terminal actions, DD/MM/YYYY input, and output callouts.
- Added `demo/run_demo.py` with `--mode live` and `--mode mock` plus `--store memory|cosmos` for no-Azure fallback paths.
- Added `demo/sample_output.md` with deterministic sections for failure event, analyzer findings, diagnosis, and fix diff.
- Verified `--mode live --store memory` exercises FailureDetector -> TraceStore -> IndaginePipeline -> DiagnosisEngine -> FixGenerator.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write a time-boxed 2-minute demo scenario script** - `37f8d3f` (feat)
2. **Task 2: Add a demo runner with a mock/fallback mode** - `a9aa185` (feat)

**Plan metadata:** Pending (created after summary/state updates)

## Files Created/Modified

- `demo/scenario.md` - 2-minute narration + command timeline for the BookingAgent date-format failure story.
- `demo/run_demo.py` - Demo CLI runner for live pipeline and fixture-backed mock output.
- `demo/sample_output.md` - Stable mock output fixture used by `--mode mock`.
- `src/storage/trace_store.py` - Lazy Cosmos import behavior so memory backend can run when Azure SDK is unavailable.

## Decisions Made

- Kept the live runner on real modules (not `run_and_capture`) by invoking `run_with_failure_detection` with `run_subject_scenario` and then passing stored traces through `IndaginePipeline`.
- Standardized mock/live output to the same top-level sections so narration and terminal highlights remain identical across fallback paths.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Live mode could not import `src` when run as `python3 demo/run_demo.py`**
- **Found during:** Task 2 verification
- **Issue:** Running the script from `demo/` context set `sys.path[0]` to `demo`, so live imports failed before pipeline execution.
- **Fix:** Prepended repository root to `sys.path` inside `demo/run_demo.py`.
- **Files modified:** `demo/run_demo.py`
- **Verification:** `python3 demo/run_demo.py --mode mock` and `.venv/bin/python demo/run_demo.py --mode live --store memory` both ran.
- **Committed in:** `a9aa185`

**2. [Rule 3 - Blocking] Memory TraceStore path still required Azure SDK imports**
- **Found during:** Task 2 verification
- **Issue:** `src/storage/trace_store.py` eagerly imported cosmos client modules, breaking memory-only runs on machines without Azure packages.
- **Fix:** Lazy-loaded cosmos settings/client only when selecting cosmos backend; memory backend now works independently.
- **Files modified:** `src/storage/trace_store.py`
- **Verification:** `.venv/bin/python demo/run_demo.py --mode live --store memory` succeeded end-to-end.
- **Committed in:** `a9aa185`

**3. [Rule 3 - Blocking] System Python lacks runtime dependencies for live mode**
- **Found during:** Task 2 verification
- **Issue:** `python3 demo/run_demo.py --mode live --store memory` failed due missing `opentelemetry` in system interpreter.
- **Fix:** Verified live mode with project runtime (`.venv/bin/python ...`) and documented this in demo script/setup.
- **Files modified:** None (environment-only)
- **Verification:** `.venv/bin/python demo/run_demo.py --mode live --store memory`
- **Committed in:** N/A

---

**Total deviations:** 3 auto-fixed (3 blocking)
**Impact on plan:** All fixes were required to guarantee a reliable no-Azure demo flow and did not change planned scope.

## Authentication Gates

None.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- DEMO-01 foundation is complete with a rehearsable script and repeatable runner.
- Ready for 04-02 video capture using live memory mode, with mock fallback available.

---
*Phase: 04-demo-submit*
*Completed: 2026-02-11*

## Self-Check: PASSED

- Verified output files exist: `demo/scenario.md`, `demo/run_demo.py`, `demo/sample_output.md`, `.planning/phases/04-demo-submit/04-01-SUMMARY.md`.
- Verified task commits exist in git history: `37f8d3f`, `a9aa185`.
