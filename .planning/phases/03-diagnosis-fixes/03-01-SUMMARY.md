---
phase: 03-diagnosis-fixes
plan: "01"
subsystem: diagnosis
tags: [python, pydantic, diagnosis-engine, failure-taxonomy, pytest]

requires:
  - phase: 02-03
    provides: Unified FindingsReport output from TraceAnalyzer and ToolAnalyzer orchestration
provides:
  - Deterministic DiagnosisEngine classification for all six failure taxonomy types
  - Strict Diagnosis model with confidence scoring and linkable similar failure IDs
  - Fixture-driven tests validating taxonomy coverage and link-count consistency
affects: [03-diagnosis-fixes, 04-demo-submit]

tech-stack:
  added: []
  patterns:
    [deterministic signal-based diagnosis, strict pydantic diagnosis contract, fixture-driven taxonomy verification]

key-files:
  created:
    - src/models/diagnosis.py
    - src/core/diagnosis_engine.py
    - tests/fixtures/findings/booking_findings.json
    - tests/fixtures/findings/context_overflow_findings.json
    - tests/fixtures/findings/coordination_findings.json
    - tests/fixtures/findings/reasoning_error_findings.json
    - tests/fixtures/findings/search_findings.json
    - tests/fixtures/findings/summary_findings.json
    - tests/test_diagnosis_engine.py
  modified: []

key-decisions:
  - "Diagnosis.similar_past_failures is a computed field derived from similar_past_failure_ids to guarantee count consistency."
  - "DiagnosisEngine uses fixed-priority deterministic markers (tool misuse > hallucination > prompt ambiguity > context overflow > coordination > fallback)."

patterns-established:
  - "DiagnosisEngine consumes FindingsReport directly and outputs a strict Diagnosis contract."
  - "Diagnosis fixtures encode stable marker tokens to guarantee deterministic taxonomy outcomes in tests."

duration: 8 min
completed: 2026-02-11
---

# Phase 3 Plan 1: Diagnosis Engine Taxonomy Summary

**Deterministic diagnosis now maps analyzer findings to all six FailureTaxonomy root causes with confidence, explanations, affected subjects, and linkable similar failure IDs.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-02-11T04:00:35Z
- **Completed:** 2026-02-11T04:09:10Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- Added `FailureTaxonomy` and strict `Diagnosis` output contract in `src/models/diagnosis.py`.
- Implemented `DiagnosisEngine` in `src/core/diagnosis_engine.py` with deterministic, explainable root-cause classification.
- Added six findings fixtures and diagnosis tests proving full taxonomy coverage and `similar_past_failures`/ID consistency.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add diagnosis models including failure taxonomy enum** - `31b8b52` (feat)
2. **Task 2: Implement DiagnosisEngine with deterministic rule-based classification** - `5d7e74e` (feat)

**Plan metadata:** Pending (created after summary/state/roadmap updates)

## Files Created/Modified
- `src/models/diagnosis.py` - Defines the strict diagnosis contract and six-value taxonomy enum.
- `src/core/diagnosis_engine.py` - Implements deterministic rule-based diagnosis from `FindingsReport`.
- `tests/fixtures/findings/booking_findings.json` - TOOL_MISUSE fixture with schema mismatch marker.
- `tests/fixtures/findings/search_findings.json` - PROMPT_AMBIGUITY fixture with missing-info/multiple-interpretations markers.
- `tests/fixtures/findings/summary_findings.json` - HALLUCINATION fixture with `hallucinated=true` marker.
- `tests/fixtures/findings/context_overflow_findings.json` - CONTEXT_OVERFLOW fixture with stable overflow tokens.
- `tests/fixtures/findings/coordination_findings.json` - COORDINATION_FAILURE fixture with handoff/agent markers.
- `tests/fixtures/findings/reasoning_error_findings.json` - REASONING_ERROR fallback fixture without stronger markers.
- `tests/test_diagnosis_engine.py` - Fixture-driven tests for taxonomy coverage and linked-failure count consistency.

## Decisions Made
- Derived `similar_past_failures` from `similar_past_failure_ids` as a computed field to satisfy DIAG-04 linkability without drift.
- Used explicit marker priority ordering so diagnosis outputs remain deterministic across mixed-signal findings.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] System Python lacks pytest for required verification command**
- **Found during:** Task 2 verification and final plan verification
- **Issue:** `python3 -m pytest -q` fails with `No module named pytest` in this environment.
- **Fix:** Executed equivalent verification via project virtualenv: `.venv/bin/python -m pytest -q`.
- **Files modified:** None (runtime environment only)
- **Verification:** `.venv/bin/python -m pytest -q` passed (`31 passed`).
- **Committed in:** N/A (no repository file change)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change; deviation only affected command runner selection.

## Authentication Gates
None.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Diagnosis taxonomy foundation is complete and deterministic; ready for `03-02-PLAN.md` (fix generation).
- Environment caveat remains: use `.venv/bin/python -m ...` for deterministic verification in this workspace.

---
*Phase: 03-diagnosis-fixes*
*Completed: 2026-02-11*

## Self-Check: PASSED

- Verified summary and all key output files exist on disk.
- Verified task commits exist in git history: `31b8b52`, `5d7e74e`.
