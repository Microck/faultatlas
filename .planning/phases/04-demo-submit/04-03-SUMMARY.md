---
phase: 04-demo-submit
plan: "03"
subsystem: docs
tags: [demo, submission, checklist, recording]

# Dependency graph
requires:
  - phase: 04-01
    provides: demo scenario script and live/mock runner commands used for recording steps
  - phase: 04-02
    provides: README, architecture, and taxonomy artifacts referenced by submission checklist
provides:
  - Recording checklist with pre-flight checks, ordered commands, visual callouts, and export requirements
  - Submission checklist linking core artifacts and final portal-ready requirement checks
affects: [demo-recording, submission-package, hackathon-portal]

# Tech tracking
tech-stack:
  added: [none]
  patterns:
    - checklist-driven demo packaging with explicit verification items
    - live-first demo command path with documented mock fallback for reliability

key-files:
  created: [demo/recording_checklist.md, demo/submission_checklist.md]
  modified: [none]

key-decisions:
  - "Recording checklist explicitly follows demo/scenario.md and prioritizes `.venv/bin/python demo/run_demo.py --mode live --store memory` with immediate mock fallback."
  - "Submission checklist references both docs/architecture.png and docs/architecture.mmd so packaging remains complete even if raster export is unavailable."

patterns-established:
  - "Submission prep artifacts live under demo/ as actionable checklists with binary completion states."
  - "Final packaging checks reference repository-local paths to speed judge and reviewer navigation."

# Metrics
duration: 33 min
completed: 2026-02-11
---

# Phase 04 Plan 03: Recording and Submission Checklist Summary

**FaultAtlas now includes execution-ready recording and submission checklists that convert the existing demo/docs artifacts into a repeatable, portal-ready handoff package.**

## Performance

- **Duration:** 33 min
- **Started:** 2026-02-11T18:11:15Z
- **Completed:** 2026-02-11T18:44:42Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added `demo/recording_checklist.md` with pre-flight setup, exact command order, visual callouts, and MP4 export requirements.
- Added `demo/submission_checklist.md` with required artifact links and a final readiness checklist for hackathon submission packaging.
- Preserved live-demo-first guidance while making mock fallback explicit to keep recording non-blocking.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create recording checklist (manual step, non-blocking)** - `efcdeec` (feat)
2. **Task 2: Create submission checklist** - `bccf672` (feat)

**Plan metadata:** Pending (created after summary/state updates)

## Files Created/Modified

- `demo/recording_checklist.md` - Step-by-step recording runbook tied to `demo/scenario.md`, including fallback and export targets.
- `demo/submission_checklist.md` - Final packaging checklist covering required files, video expectations, and submission-form readiness.

## Decisions Made

- Anchored recording flow to the existing scripted narration (`demo/scenario.md`) to keep the live capture aligned with earlier demo planning.
- Included both architecture artifact paths (`docs/architecture.png` and `docs/architecture.mmd`) to prevent submission blockage in headless environments.

## Deviations from Plan

None - plan executed exactly as written.

## Authentication Gates

None.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 4 plan execution is complete and all checklist artifacts are in place.
- Manual steps remain outside this plan: record `demo/video.mp4` and submit final links in the hackathon portal.

## Self-Check: PASSED

- FOUND: `demo/recording_checklist.md`
- FOUND: `demo/submission_checklist.md`
- FOUND commit: `efcdeec`
- FOUND commit: `bccf672`

---
*Phase: 04-demo-submit*
*Completed: 2026-02-11*
