# Indagine

## What This Is

A meta-agent system that automatically debugs other AI agents when they fail. When an agent in a multi-agent system fails, Indagine detects the failure, analyzes execution traces, diagnoses the root cause using a failure taxonomy, suggests concrete fixes, and validates the fixes by re-running the failed scenario. Built for the Microsoft AI Dev Days Hackathon 2026.

## Core Value

**When an AI agent fails, another agent must be able to diagnose WHY it failed and suggest a fix — automatically, without human trace analysis.**

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Test subject agents that fail predictably (BookingAgent, SearchAgent, SummaryAgent)
- [ ] Failure detection via Foundry tracing hooks
- [ ] Trace Analyzer agent that parses execution traces and finds failure points
- [ ] Tool Analyzer agent that validates tool usage against schemas
- [ ] Prompt Analyzer agent that checks for ambiguity and missing context
- [ ] Indagine Controller that orchestrates analysis agents
- [ ] Diagnosis Engine with 6-type failure taxonomy
- [ ] Fix Generator that proposes prompt/config/guardrail changes
- [ ] Validation Loop that re-runs scenarios with fixes applied
- [ ] 2-minute demo video showing end-to-end flow

### Out of Scope

- Production deployment — hackathon demo only
- Self-healing without human approval — fixes require confirmation
- Real-time monitoring dashboard — focus on core diagnosis flow
- Support for non-Foundry tracing systems — tight Azure integration
- Code-level bug fixing — this is agent-level debugging, not code repair

## Context

**Hackathon:** Microsoft AI Dev Days 2026 (Feb 10 - Mar 15, 2026)

**Target Prizes:**
- Primary: AI Apps & Agents ($20,000)
- Secondary: Foundry ($10,000)
- Tertiary: Multi-Agent ($10,000)

**Prior Art:**
- RepairAgent: Fixes CODE bugs (we fix AGENT failures)
- Evolver (aiXplain): Optimizes prompts (we diagnose failures, not optimize)
- InspectCoder: LLM + debugger (code-level, not agent-level)
- Reflexion/Self-Refine: Self-correction patterns (generic technique, not productized)

**Novelty:**
- First meta-agent that monitors OTHER agents in a multi-agent system
- Diagnosis of agent-specific failure modes (not code bugs)
- Fixes to agent CONFIGURATION, not just code
- Deep integration with Foundry's tracing/observability

**Failure Taxonomy:**
1. PROMPT_AMBIGUITY — unclear instructions, missing context
2. TOOL_MISUSE — wrong tool, invalid parameters
3. HALLUCINATION — made up information, fabricated results
4. CONTEXT_OVERFLOW — lost context, forgot instructions
5. REASONING_ERROR — flawed logic, wrong conclusions
6. COORDINATION_FAILURE — agent handoff broke, state lost

## Constraints

- **Timeline**: 5 weeks (Feb 10 - Mar 15, 2026)
- **Tech Stack**: Python, Microsoft Agent Framework, Azure AI Foundry
- **Model Access**: GPT-4o via Foundry
- **Storage**: Azure Cosmos DB (failures), Azure AI Search (RAG over past fixes)
- **Tracing**: Must use Foundry Observability for trace capture
- **Demo**: 2-minute video required for submission

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Focus on TOOL_MISUSE first | Most concrete failure type, easiest to demo | — Pending |
| 8 specialized agents | Clear separation of concerns, impressive multi-agent architecture | — Pending |
| Python over TypeScript | Better Azure SDK support, faster prototyping | — Pending |
| Validation Loop optional | Can cut if time runs short, demo still works with suggestions only | — Pending |

---
*Last updated: 2026-02-08 after project initialization*
