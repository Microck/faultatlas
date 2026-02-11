---
phase: 02-analysis-pipeline
plan: "02"
subsystem: analysis
tags: [python, jsonschema, tool-analysis, fixture-driven-tests, pytest]

requires:
  - phase: 02-01
    provides: Trace/finding contracts and deterministic trace analyzer outputs
provides:
  - Shared SchemaRegistry for tool schema lookup across subjects and analyzers
  - ToolAnalyzer that reports schema mismatches from trace tool calls
  - Wrong-tool detection for SearchAgent traces via metadata and fallback heuristic
affects: [02-analysis-pipeline, 03-diagnosis-fixes]

tech-stack:
  added: []
  patterns:
    [shared schema registry abstraction, mismatch-first tool analysis, fixture-driven wrong-tool regression tests]

key-files:
  created:
    - src/tools/schema_registry.py
    - src/analyzers/tool_analyzer.py
    - tests/fixtures/traces/tool_calls_search.json
    - tests/test_tool_analyzer.py
  modified:
    - src/tools/registry.py

key-decisions:
  - "SchemaRegistry.validate returns structured mismatch records while ToolRegistry keeps raising ToolValidationError for subject scenarios."
  - "Wrong-tool detection prioritizes metadata intended_tool and falls back to a search-intent heuristic when metadata is missing."

patterns-established:
  - "ToolAnalyzer normalizes tool calls from both step.tool_calls and step.output.tool_calls."
  - "Tool misuse findings are emitted as stable ToolFinding payloads with schema mismatch and wrong-tool fields."

duration: 5 min
completed: 2026-02-11
---

# Phase 2 Plan 2: Tool Analyzer and Schema Registry Summary

**Tool misuse is now diagnosable from trace data via schema-backed argument validation and deterministic wrong-tool detection in SearchAgent scenarios.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-11T02:15:36Z
- **Completed:** 2026-02-11T02:21:10Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Added `src/tools/schema_registry.py` as the shared schema lookup and validation source for analyzers and subjects.
- Refactored `src/tools/registry.py` into a thin compatibility wrapper that preserves existing `ToolValidationError` behavior.
- Implemented `src/analyzers/tool_analyzer.py` to report schema mismatches and wrong-tool selection in trace tool calls.
- Added SearchAgent-focused fixture and unit tests that assert schema mismatch detection and wrong-tool flags.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement SchemaRegistry shared by subjects + analyzers** - `9c9d4bf` (feat)
2. **Task 2: Implement ToolAnalyzer + tests using tool-call fixtures** - `58e74e6` (feat)

**Plan metadata:** Pending (created after summary/state updates)

## Files Created/Modified
- `src/tools/schema_registry.py` - Central schema loading, tool listing, schema lookup, and mismatch reporting.
- `src/tools/registry.py` - Compatibility wrapper preserving public validation behavior for subject scenarios.
- `src/analyzers/tool_analyzer.py` - Tool-call analysis with schema mismatch and wrong-tool detection logic.
- `tests/fixtures/traces/tool_calls_search.json` - SearchAgent trace fixture with tool-call records for misuse analysis.
- `tests/test_tool_analyzer.py` - Tests verifying schema mismatch detection and wrong-tool selection flags.

## Decisions Made
- Schema validation internals were centralized in `SchemaRegistry`, while subject-facing failure contracts remained unchanged through `ToolRegistry`.
- Wrong-tool detection was implemented as a two-step strategy: metadata comparison first, then a deterministic SearchAgent fallback heuristic.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] System Python lacks pytest for required verification command**
- **Found during:** Task 2 verification and plan-level verification
- **Issue:** `python3 -m pytest -q` fails with `No module named pytest` in the system Python runtime.
- **Fix:** Executed verification with the project virtual environment using `.venv/bin/python -m pytest -q`.
- **Files modified:** None (execution environment only)
- **Verification:** `.venv/bin/python -m pytest -q` passed (`15 passed`).
- **Committed in:** N/A (no repository file change)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change; deviation only affected command runtime selection.

## Authentication Gates
None.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Ready for `02-03-PLAN.md`: tool misuse findings now include schema mismatch and wrong-tool evidence derived from traces.
- Environment caveat remains: use `.venv/bin/python -m ...` for deterministic verification in this workspace.

---
*Phase: 02-analysis-pipeline*
*Completed: 2026-02-11*

## Self-Check: PASSED

- Verified key output files exist on disk: `src/tools/schema_registry.py`, `src/analyzers/tool_analyzer.py`, `tests/fixtures/traces/tool_calls_search.json`, `tests/test_tool_analyzer.py`.
- Verified task commits exist in git history: `9c9d4bf`, `58e74e6`.
