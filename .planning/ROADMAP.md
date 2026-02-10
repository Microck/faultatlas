# FaultAtlas Roadmap

## Overview

A meta-agent system that automatically debugs other AI agents when they fail. Built for Microsoft AI Dev Days Hackathon 2026.

**Timeline:** 5 weeks (Feb 10 - Mar 15, 2026)
**Target Prizes:** AI Apps & Agents ($20k), Foundry ($10k), Multi-Agent ($10k)

---

## Phase 1: Foundation

**Goal:** Build test subject agents that fail predictably + failure detection infrastructure

**Duration:** ~1 week

**Requirements Covered:**
- FOUND-01: Foundry project initialized with tracing enabled
- FOUND-02: BookingAgent that can fail on date format parsing
- FOUND-03: SearchAgent that can fail on wrong tool selection
- FOUND-04: SummaryAgent that can hallucinate information
- FOUND-05: Failure Detector that watches for exceptions, validation failures, timeouts
- FOUND-06: Trace capture stores execution traces to Cosmos DB

**Success Criteria:**
1. Foundry project is initialized with tracing enabled and accessible
2. BookingAgent reliably fails when given DD/MM/YYYY date format
3. SearchAgent reliably fails when given ambiguous tool selection scenario
4. SummaryAgent reliably hallucinates when given minimal source material
5. Failure Detector catches all 3 failure types and logs structured output
6. Execution traces are stored in Cosmos DB and retrievable by failure_id

**Deliverables:**
- `src/subjects/booking_agent.py` — Date parsing failure scenario
- `src/subjects/search_agent.py` — Tool selection failure scenario
- `src/subjects/summary_agent.py` — Hallucination failure scenario
- `src/core/failure_detector.py` — Failure detection hooks
- `src/storage/trace_store.py` — Cosmos DB trace storage
- `infra/foundry_config.yaml` — Foundry project configuration

---

## Phase 2: Analysis Pipeline

**Goal:** Build the multi-agent analysis system (Trace Analyzer, Tool Analyzer, Autopsy Controller)

**Duration:** ~1 week

**Requirements Covered:**
- ANLZ-01: Trace Analyzer parses execution traces and identifies failure step
- ANLZ-02: Trace Analyzer extracts reasoning chain that led to failure
- ANLZ-03: Tool Analyzer validates parameters against tool schema
- ANLZ-04: Tool Analyzer detects wrong tool selection
- ANLZ-05: Autopsy Controller orchestrates Trace and Tool analyzers
- ANLZ-06: Autopsy Controller collects findings into structured output

**Success Criteria:**
1. Trace Analyzer correctly identifies failure step (step N of M) for all 3 test subjects
2. Trace Analyzer extracts reasoning chain as structured list of steps
3. Tool Analyzer validates parameters against JSON schemas and reports mismatches
4. Tool Analyzer detects when wrong tool was selected (SearchAgent scenario)
5. Autopsy Controller orchestrates both analyzers and waits for completion
6. Autopsy Controller produces unified FindingsReport with structured output

**Deliverables:**
- `src/analyzers/trace_analyzer.py` — Trace parsing and failure point identification
- `src/analyzers/tool_analyzer.py` — Tool schema validation and selection detection
- `src/core/autopsy_controller.py` — Multi-agent orchestration
- `src/models/findings.py` — Pydantic models for structured findings
- `tests/test_trace_analyzer.py` — Unit tests for trace parsing
- `tests/test_tool_analyzer.py` — Unit tests for tool validation

---

## Phase 3: Diagnosis & Fixes

**Goal:** Root cause diagnosis with failure taxonomy + fix generation

**Duration:** ~1.5 weeks

**Requirements Covered:**
- DIAG-01: Diagnosis Engine implements 6-type failure taxonomy
- DIAG-02: Diagnosis Engine identifies root cause from analyzer findings
- DIAG-03: Diagnosis Engine provides explanation of what went wrong
- DIAG-04: Diagnosis Engine links to similar past failures (if any)
- FIX-01: Fix Generator proposes PROMPT_FIX changes (add instructions/examples)
- FIX-02: Fix Generator proposes TOOL_CONFIG_FIX changes (add validation/transformation)
- FIX-03: Fix Generator proposes GUARDRAIL_FIX changes (add output validation/retry)
- FIX-04: Fix Generator shows exact diff of proposed changes

**Success Criteria:**
1. Diagnosis Engine correctly classifies failures into taxonomy (TOOL_MISUSE, HALLUCINATION, etc.)
2. Diagnosis Engine produces root_cause with confidence score (0.0-1.0)
3. Diagnosis Engine generates human-readable explanation of what went wrong
4. Diagnosis Engine queries past failures and links similar cases (even if 0 matches initially)
5. Fix Generator produces at least one proposed fix for each failure type
6. Fix Generator shows before/after diff for prompt and config changes

**Deliverables:**
- `src/core/diagnosis_engine.py` — Failure taxonomy and root cause identification
- `src/core/fix_generator.py` — Fix proposal generation
- `src/models/diagnosis.py` — Pydantic models for diagnosis output
- `src/models/fixes.py` — Pydantic models for fix proposals
- `src/storage/fix_history.py` — Past fix lookup (Cosmos DB)
- `tests/test_diagnosis_engine.py` — Unit tests for diagnosis
- `tests/test_fix_generator.py` — Unit tests for fix generation

---

## Phase 4: Demo & Submit

**Goal:** Polished demo video, documentation, and submission package

**Duration:** ~1.5 weeks

**Requirements Covered:**
- DEMO-01: Scripted demo scenario with BookingAgent date format failure
- DEMO-02: 2-minute video showing: failure → analysis → diagnosis → fix suggestion
- DEMO-03: README with project overview, architecture, and setup instructions
- DEMO-04: Architecture diagram showing all 8 agents and data flow

**Success Criteria:**
1. Demo script is written and rehearsed (BookingAgent date format scenario)
2. 2-minute video is recorded showing end-to-end flow with voice-over
3. README includes: overview, architecture, setup, usage, and demo instructions
4. Architecture diagram (PNG/SVG) shows all agents and data flow clearly
5. Submission package passes all hackathon requirements

**Deliverables:**
- `demo/scenario.md` — Scripted demo scenario
- `demo/video.mp4` — 2-minute demo video
- `README.md` — Project documentation
- `docs/architecture.png` — Architecture diagram
- `docs/failure_taxonomy.md` — Failure taxonomy documentation
- Submission to hackathon portal

---

## Phase Dependencies

```
Phase 1 (Foundation)
    │
    ▼
Phase 2 (Analysis Pipeline)
    │
    ▼
Phase 3 (Diagnosis & Fixes)
    │
    ▼
Phase 4 (Demo & Submit)
```

All phases are sequential. Each phase builds on the deliverables of the previous phase.

---

## v2 Requirements (Post-v1)

These requirements are deferred to after v1 is complete:

| Requirement | Phase | Notes |
|------------|-------|-------|
| Prompt Analyzer | v2 | Third analyzer for ambiguity detection |
| Confidence scoring | v2 | Adds precision to diagnosis |
| Validation Loop | v2 | Re-run with fix applied |
| Fix history RAG | v2 | Azure AI Search index |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Scope creep | Focus on TOOL_MISUSE first, it's most concrete |
| Foundry tracing gaps | Add custom logging if needed |
| Time pressure | Validation Loop is optional, demo works without it |
| Fix suggestions wrong | Human approval required, never auto-apply |

---

## Coverage Validation

All 20 v1 requirements are mapped:
- Phase 1: FOUND-01 through FOUND-06 (6 requirements)
- Phase 2: ANLZ-01 through ANLZ-06 (6 requirements)
- Phase 3: DIAG-01 through DIAG-04, FIX-01 through FIX-04 (8 requirements)
- Phase 4: DEMO-01 through DEMO-04 (4 requirements)

**Total: 20/20 requirements covered (100%)**

---

*Last updated: 2026-02-08*
