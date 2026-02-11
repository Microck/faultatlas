---
phase: 03-diagnosis-fixes
verified: 2026-02-11T04:42:05Z
status: human_needed
score: 7/7 must-haves verified
human_verification:
  - test: "Run Cosmos-backed similarity roundtrip"
    expected: "With COSMOS_* configured, FixHistory(backend='cosmos') stores and returns matching failure_ids via find_similar(...)"
    why_human: "Requires live Azure Cosmos credentials/resources not available in verifier environment"
  - test: "Run DiagnosisEngine + Cosmos FixHistory integration"
    expected: "DiagnosisEngine(fix_history=FixHistory(backend='cosmos')).diagnose(...) populates similar_past_failure_ids when matching history exists"
    why_human: "External service integration cannot be validated in offline/static checks"
---

# Phase 3: Diagnosis & Fixes Verification Report

**Phase Goal:** Root cause diagnosis with failure taxonomy + fix generation
**Verified:** 2026-02-11T04:42:05Z
**Status:** human_needed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Diagnosis Engine emits all 6 taxonomy types from deterministic signals | ✓ VERIFIED | Taxonomy enum has 6 required values in `src/models/diagnosis.py:8`; deterministic classifier branches in `src/core/diagnosis_engine.py:90`; suite asserts full set coverage in `tests/test_diagnosis_engine.py:48` |
| 2 | Diagnosis output always includes `root_cause`, `confidence`, and `explanation` | ✓ VERIFIED | Model contract fields in `src/models/diagnosis.py:20`; engine populates values in `src/core/diagnosis_engine.py:60`; assertions in `tests/test_diagnosis_engine.py:43` |
| 3 | Diagnosis output includes linkable similar failure IDs and count consistency | ✓ VERIFIED | `similar_past_failure_ids` + computed count in `src/models/diagnosis.py:25`; lookup result is written into diagnosis in `src/core/diagnosis_engine.py:69`; consistency asserted in `tests/test_diagnosis_engine.py:57` |
| 4 | Diagnosis can return non-empty similar failure IDs when history has matches | ✓ VERIFIED | `find_similar(...)` dependency call in `src/core/diagnosis_engine.py:69`; verifier execution artifact: `ids=['hist-1']; count=1` using `DiagnosisEngine(fix_history=FixHistory(backend='memory'))` |
| 5 | Fix Generator proposes at least one fix for each taxonomy type | ✓ VERIFIED | Taxonomy-to-template routing in `src/core/fix_generator.py:19`; per-taxonomy non-empty assertions in `tests/test_fix_generator.py:46` |
| 6 | Each proposed change includes a unified before/after diff | ✓ VERIFIED | Unified diff utility in `src/core/diff_utils.py:6`; diff attached in `src/core/fix_generator.py:185`; diff header assertions in `tests/test_fix_generator.py:61` |
| 7 | Fix history works without Azure via in-memory backend | ✓ VERIFIED | In-memory persistence/query implementation in `src/storage/fix_history_memory.py:35`; expected ID matching and limit behavior in `tests/test_fix_history_memory.py:31` |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `src/models/diagnosis.py` | Diagnosis taxonomy + output contract | ✓ VERIFIED | Exists (31 lines), strict Pydantic config, no stub markers; consumed by diagnosis/fix/storage modules |
| `src/core/diagnosis_engine.py` | Root-cause diagnosis from findings | ✓ VERIFIED | Exists (228 lines), deterministic multi-signal classification and similarity lookup wiring |
| `src/models/fixes.py` | Fix proposal contract | ✓ VERIFIED | Exists (31 lines), concrete FixType/FixChange/FixProposal models, no placeholders |
| `src/core/diff_utils.py` | Unified diff generation | ✓ VERIFIED | Exists (21 lines), stdlib `difflib.unified_diff` wrapper with guardrails |
| `src/core/fix_generator.py` | Taxonomy-driven fix proposal generation | ✓ VERIFIED | Exists (194 lines), proposal templates for all 6 taxonomy values, wired to diff utility |
| `src/storage/fix_history.py` | Backend facade for memory/cosmos fix history | ✓ VERIFIED | Exists (245 lines), record/query API + auto backend selection + Cosmos query implementation |
| `src/storage/fix_history_memory.py` | Local/in-test fix history backend | ✓ VERIFIED | Exists (105 lines), record failure/fix + similarity query with limit support |
| `tests/test_diagnosis_engine.py` | Diagnosis behavior verification | ✓ VERIFIED | Exists (64 lines), validates deterministic classification, confidence bounds, link-count consistency |
| `tests/test_fix_generator.py` | Fix generation behavior verification | ✓ VERIFIED | Exists (90 lines), validates taxonomy coverage and diff structure |
| `tests/test_fix_history_memory.py` | History lookup behavior verification | ✓ VERIFIED | Exists (76 lines), validates root_cause/sub_type matching and limit behavior |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `src/core/diagnosis_engine.py` | `src/models/findings.py` | `FindingsReport.model_validate(...)` and typed partitioning | WIRED | Input contract enforcement in `src/core/diagnosis_engine.py:54`; typed `TraceFinding`/`ToolFinding` partition in `src/core/diagnosis_engine.py:72` |
| `src/core/diagnosis_engine.py` | `src/storage/fix_history.py` | injected `find_similar(...)` lookup | WIRED | Protocol call and response usage in `src/core/diagnosis_engine.py:69`; verifier integration artifact with `FixHistory(backend='memory')` returned linked IDs |
| `src/core/fix_generator.py` | `src/core/diff_utils.py` | `unified_diff(...)` per change | WIRED | `_change(...)` computes and stores diff in `src/core/fix_generator.py:179`; diff utility implementation in `src/core/diff_utils.py:6` |
| `src/storage/fix_history.py` | `src/storage/fix_history_memory.py` | auto/default memory backend fallback | WIRED | Backend selection in `src/storage/fix_history.py:206`; verifier artifact `FixHistory().backend_name -> memory` |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
| --- | --- | --- |
| DIAG-01: 6-type failure taxonomy | ✓ SATISFIED | None |
| DIAG-02: root cause identification from findings + confidence | ✓ SATISFIED | None |
| DIAG-03: human-readable explanation | ✓ SATISFIED | None |
| DIAG-04: links to similar past failures | ✓ SATISFIED | Cosmos-backed live verification still requires human run |
| FIX-01: PROMPT_FIX proposals | ✓ SATISFIED | None |
| FIX-02: TOOL_CONFIG_FIX proposals | ✓ SATISFIED | None |
| FIX-03: GUARDRAIL_FIX proposals | ✓ SATISFIED | None |
| FIX-04: exact before/after diff output | ✓ SATISFIED | None |

### Execution Artifacts Checked

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest -q tests/test_diagnosis_engine.py tests/test_fix_generator.py tests/test_fix_history_memory.py` | `28 passed in 0.30s` |
| `.venv/bin/python -m pytest -q` | `46 passed in 0.87s` |
| `DiagnosisEngine(fix_history=FixHistory(backend='memory')).diagnose(booking_fixture)` | `ids=['hist-1']; count=1` |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| `src/core/fix_generator.py` | 32 | `return []` fallback | ℹ️ Info | Defensive fallback for unknown taxonomy; tests cover all known taxonomy values |
| `src/storage/fix_history.py` | 172 | `return []` for `limit <= 0` | ℹ️ Info | Guard clause, not a stub path |
| `src/storage/fix_history_memory.py` | 85 | `return []` for `limit <= 0` | ℹ️ Info | Guard clause, not a stub path |

### Human Verification Required

### 1. Cosmos Similarity Roundtrip

**Test:** Configure `COSMOS_ENDPOINT`, `COSMOS_KEY`, `COSMOS_DATABASE`, and `COSMOS_CONTAINER_FIXES`; then run a script that calls `FixHistory(backend='cosmos').record_failure(...)` followed by `find_similar(...)`.
**Expected:** Matching `failure_id` values are returned for same `root_cause` + `sub_type`.
**Why human:** Requires live Azure Cosmos account/credentials and cloud network access.

### 2. Diagnosis Engine + Cosmos Link Injection

**Test:** Instantiate `DiagnosisEngine(fix_history=FixHistory(backend='cosmos'))` and diagnose a fixture with known matching history.
**Expected:** `diagnosis.similar_past_failure_ids` is non-empty and `similar_past_failures == len(similar_past_failure_ids)`.
**Why human:** End-to-end external service wiring cannot be proven by static checks in this environment.

### Gaps Summary

No code-level gaps were found for DIAG-01..DIAG-04 and FIX-01..FIX-04. Phase implementation is complete in code and tests. Remaining work is external-service verification for Cosmos-backed similarity lookup.

---

_Verified: 2026-02-11T04:42:05Z_
_Verifier: Claude (gsd-verifier)_
