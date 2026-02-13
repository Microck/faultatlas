# Indagine Failure Taxonomy

This taxonomy is the shared diagnosis vocabulary used by `DiagnosisEngine` and `FixGenerator`.

## 1) PROMPT_AMBIGUITY
- **Symptoms:** Instructions can be interpreted in multiple ways; agent behavior varies across similar inputs.
- **Detection signals:** Ambiguous language in prompts, missing constraints/examples, analyzer notes about unclear intent.
- **Typical fixes:** Add explicit constraints and examples; restate expected output format.

## 2) TOOL_MISUSE
- **Symptoms:** Wrong tool selected, invalid parameters, or schema/format errors during tool calls.
- **Detection signals:** Tool schema validation errors, mismatch between intended tool and invoked tool.
- **Typical fixes:** Add pre-call validation/transformation; tighten tool-selection rules.

## 3) HALLUCINATION
- **Symptoms:** Agent returns confident claims not supported by trace, tools, or provided sources.
- **Detection signals:** Missing source attribution, statements that cannot be grounded in retrieved data.
- **Typical fixes:** Require source-backed outputs; add guardrails that reject ungrounded claims.

## 4) CONTEXT_OVERFLOW
- **Symptoms:** Agent forgets earlier constraints or drops critical context mid-flow.
- **Detection signals:** Long traces with lost instructions, outputs that ignore earlier required details.
- **Typical fixes:** Summarize and pin critical context; reduce prompt/token footprint before key steps.

## 5) REASONING_ERROR
- **Symptoms:** Agent has relevant data but reaches incorrect conclusions or skips logical steps.
- **Detection signals:** Inconsistent reasoning chain between evidence and final output.
- **Typical fixes:** Enforce stepwise reasoning checks; add intermediate validation before final answer.

## 6) COORDINATION_FAILURE
- **Symptoms:** Handoff between agents breaks, shared state is lost, or sequencing is incorrect.
- **Detection signals:** Missing/invalid handoff payloads, timeout patterns, inconsistent cross-agent state.
- **Typical fixes:** Standardize handoff contracts; add retry/idempotency and state validation at boundaries.
