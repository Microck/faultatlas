---
phase: 03-diagnosis-fixes
plan: "02"
subsystem: fixes
tags: [python, pydantic, difflib, fix-generator, pytest]

requires:
  - phase: 03-01
    provides: Deterministic diagnosis taxonomy classification used to drive fix proposals
provides:
  - Fix proposal contract with prompt/tool/guardrail fix types and per-change unified diffs
  - Taxonomy-driven FixGenerator that emits reviewable proposals for all six failure types
  - Fixture-driven tests validating fix coverage, diff shape, and fix-type diversity
affects: [03-diagnosis-fixes, 04-demo-submit]

tech-stack:
  added: []
  patterns: [taxonomy-to-template fix generation, unified diff artifacts for human review]

key-files:
  created:
    - src/models/fixes.py
    - src/core/diff_utils.py
    - src/core/fix_generator.py
    - tests/test_fix_generator.py
  modified: []

key-decisions:
  - "Mapped each FailureTaxonomy root cause to a deterministic fix template with explicit target file and rationale."
  - "Generated proposal diffs with stdlib difflib unified format using a/b file headers for direct reviewability."

patterns-established:
  - "Fix proposals remain non-destructive: suggest before/after snippets and diff artifacts without applying changes."
  - "Taxonomy fixture suites must prove proposal coverage and diff quality for every root cause type."

duration: 7 min
completed: 2026-02-11
---

# Phase 3 Plan 2: Fix Generator Proposal Summary

**Fix generation now produces taxonomy-specific prompt/tool/guardrail proposals with explicit before/after snippets and unified diffs for human approval.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-02-11T04:13:04Z
- **Completed:** 2026-02-11T04:20:29Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Added `src/models/fixes.py` with strict FixType/FixChange/FixProposal contracts for reviewable change proposals.
- Implemented `src/core/diff_utils.py` and `src/core/fix_generator.py` to emit unified diffs and taxonomy-aware fix proposals.
- Added `tests/test_fix_generator.py` with fixture-driven assertions for all six taxonomy types, diff headers, and fix-type coverage.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define FixProposal models (PROMPT_FIX / TOOL_CONFIG_FIX / GUARDRAIL_FIX)** - `ccc0c22` (feat)
2. **Task 2: Implement diff utils + FixGenerator and cover with tests** - `fd16583` (feat)

**Plan metadata:** Pending (created after summary/state/roadmap updates)

## Files Created/Modified
- `src/models/fixes.py` - Defines fix proposal schema and fix category enum.
- `src/core/diff_utils.py` - Provides unified diff generation for before/after proposal snippets.
- `src/core/fix_generator.py` - Maps diagnosis taxonomy to concrete prompt/tool/guardrail fix proposals.
- `tests/test_fix_generator.py` - Validates taxonomy-wide proposal coverage and diff formatting guarantees.

## Decisions Made
- Kept fix generation deterministic and template-driven so each failure taxonomy value always yields at least one reviewable proposal.
- Generated diff artifacts from the exact `before`/`after` strings embedded in each change to preserve auditability.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] System Python lacks pytest for required verification command**
- **Found during:** Task 2 verification and plan-level verification
- **Issue:** `python3 -m pytest -q` fails with `No module named pytest` in this environment.
- **Fix:** Re-ran verification with project virtualenv: `.venv/bin/python -m pytest -q`.
- **Files modified:** None (runtime environment only)
- **Verification:** `.venv/bin/python -m pytest -q` passed (`44 passed`).
- **Committed in:** N/A (no repository file change)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change; deviation only changed the Python runner used for verification.

## Authentication Gates
None.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- FIX-01 through FIX-04 contracts are now covered with deterministic proposal generation and diff output.
- Ready for `03-03-PLAN.md` to integrate fix history/lookup and complete phase-level diagnostics flow.
- Environment caveat remains: use `.venv/bin/python -m ...` for deterministic test execution in this workspace.

---
*Phase: 03-diagnosis-fixes*
*Completed: 2026-02-11*

## Self-Check: PASSED

- Verified summary and all key output files exist on disk.
- Verified task commits exist in git history: `ccc0c22`, `fd16583`.
