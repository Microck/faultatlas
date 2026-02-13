---
phase: 01-foundation
plan: "02"
subsystem: agents
tags: [python, jsonschema, cli, deterministic-tests, failure-scenarios]

requires:
  - phase: 01-01
    provides: Python scaffold, shared config conventions, and test runtime baseline
provides:
  - JSON-schema tool registry with consistent validation error metadata
  - Deterministic booking/search failure scenarios and hallucination summary scenario
  - Subject runner CLI that emits strict JSON output contracts with stable status fields
affects: [01-03, 02-analysis-pipeline]

tech-stack:
  added: []
  patterns: [schema-first tool validation, deterministic subject scenario contracts, stdout-json stderr-log CLI discipline]

key-files:
  created:
    - src/tools/registry.py
    - src/tools/schemas/search_flights.json
    - src/tools/schemas/web_search.json
    - src/tools/schemas/summarize_sources.json
    - src/subjects/booking_agent.py
    - src/subjects/search_agent.py
    - src/subjects/summary_agent.py
    - src/subjects/run_subjects.py
    - tests/test_subject_failures.py
  modified: []

key-decisions:
  - "Kept booking/search scenario functions pure and failing by raising ToolValidationError directly."
  - "Normalized runner contract to report failed/hallucinated states in JSON while always exiting 0."

patterns-established:
  - "Scenario modules expose payload builders plus deterministic run_*_scenario entrypoints."
  - "Validation failures are represented by ToolValidationError.to_dict() for downstream trace tooling."

duration: 5 min
completed: 2026-02-11
---

# Phase 1 Plan 2: Deterministic Subject Scenarios Summary

**Deterministic booking/search validation failures and a reproducible hallucination scenario now produce stable JSON outputs for Indagine pipeline inputs.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-11T01:11:16Z
- **Completed:** 2026-02-11T01:16:17Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments
- Added a schema-backed tool registry that validates payloads and emits consistent error metadata.
- Implemented booking/search/summary subject scenarios with deterministic failure and hallucination behavior.
- Added a runner CLI and smoke tests that enforce stable output contracts for downstream analyzers.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add JSON-schema tool registry used by subject scenarios** - `dd812c1` (feat)
2. **Task 2: Implement subject agents + a runner that triggers predictable failures** - `ef9e506` (feat)
3. **Task 3: Add a single smoke test asserting failure determinism** - `a43b036` (test)

**Plan metadata:** Pending (created in docs commit after summary/state updates)

## Files Created/Modified
- `src/tools/__init__.py` - Exposes tool registry primitives for imports.
- `src/tools/registry.py` - Loads schemas, validates tool calls, and raises stable ToolValidationError payloads.
- `src/tools/schemas/search_flights.json` - Enforces ISO date plus minimal route fields.
- `src/tools/schemas/web_search.json` - Enforces required search query.
- `src/tools/schemas/summarize_sources.json` - Enforces non-empty source list.
- `src/subjects/booking_agent.py` - Deterministic date-format failure scenario.
- `src/subjects/search_agent.py` - Deterministic wrong-tool argument failure scenario.
- `src/subjects/summary_agent.py` - Deterministic hallucination output with explicit false claim marker.
- `src/subjects/run_subjects.py` - CLI dispatcher with machine-parseable JSON status contract.
- `tests/test_subject_failures.py` - Fast deterministic tests for all three scenario outcomes.

## Decisions Made
- Booking and search scenario functions intentionally raise `ToolValidationError` so tests can validate exception determinism directly.
- Runner output is the source of truth for scenario status (`failed` and `hallucinated`), while process exit remains zero to support batch automation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] System Python environment lacked pytest module**
- **Found during:** Task 3 (verification)
- **Issue:** `python3 -m pytest -q` failed with `No module named pytest` in the system-managed Python environment.
- **Fix:** Executed test verification through existing isolated virtualenv (`.venv-plan01/bin/python -m pytest -q`).
- **Files modified:** None (execution environment only)
- **Verification:** `4 passed` in virtualenv and all scenario CLI contract checks passed.
- **Committed in:** N/A (no repository file change)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope creep; workaround only changed verification runtime path.

## Authentication Gates
None.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Ready for `01-03-PLAN.md` with deterministic subject failures and stable JSON artifacts in place.
- Subject output and schema contracts are now available for failure detector and trace storage integration work.

---
*Phase: 01-foundation*
*Completed: 2026-02-11*

## Self-Check: PASSED

- Verified key artifacts exist: `src/tools/registry.py`, `src/subjects/run_subjects.py`, `tests/test_subject_failures.py`.
- Verified task commits exist in git history: `dd812c1`, `ef9e506`, `a43b036`.
