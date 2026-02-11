from __future__ import annotations

from src.core.diff_utils import unified_diff
from src.models.diagnosis import Diagnosis, FailureTaxonomy
from src.models.findings import FindingsReport
from src.models.fixes import FixChange, FixProposal, FixType


class FixGenerator:
    def generate_fixes(
        self,
        diagnosis: Diagnosis | dict[str, object],
        findings_report: FindingsReport | dict[str, object],
    ) -> list[FixProposal]:
        diagnosis_model = Diagnosis.model_validate(diagnosis)
        FindingsReport.model_validate(findings_report)

        root_cause = diagnosis_model.root_cause
        if root_cause == FailureTaxonomy.TOOL_MISUSE:
            return [self._tool_misuse_fix()]
        if root_cause == FailureTaxonomy.HALLUCINATION:
            return [self._hallucination_fix()]
        if root_cause == FailureTaxonomy.PROMPT_AMBIGUITY:
            return [self._prompt_ambiguity_fix()]
        if root_cause == FailureTaxonomy.CONTEXT_OVERFLOW:
            return [self._context_overflow_fix()]
        if root_cause == FailureTaxonomy.REASONING_ERROR:
            return [self._reasoning_error_fix()]
        if root_cause == FailureTaxonomy.COORDINATION_FAILURE:
            return [self._coordination_failure_fix()]

        return []

    def _tool_misuse_fix(self) -> FixProposal:
        file_path = "src/subjects/booking_agent.py"
        before = '    active_registry.validate_payload(payload["tool_calls"][0])'
        after = (
            '    payload["tool_calls"][0]["args"] = normalize_date_args(payload["tool_calls"][0]["args"])\n'
            '    active_registry.validate_payload(payload["tool_calls"][0])'
        )
        return self._proposal(
            fix_type=FixType.TOOL_CONFIG_FIX,
            title="Normalize booking dates before tool validation",
            rationale=(
                "Add a pre-validation transformation step so date inputs are converted to "
                "YYYY-MM-DD before calling the flight search tool."
            ),
            changes=[self._change(file_path, "insert_pre_validation", before, after)],
        )

    def _hallucination_fix(self) -> FixProposal:
        file_path = "src/subjects/summary_agent.py"
        before = (
            '        "summary": (\n'
            '            "The sources mention regular routes and ordinary fares, and they also confirm a special "\n'
            '            "promotion where every seat is free."\n'
            "        ),"
        )
        after = (
            '        "summary": (\n'
            '            "The sources mention regular routes and ordinary fares, and they also confirm a special "\n'
            '            "promotion where every seat is free."\n'
            "        ),\n"
            '        "citations": [],\n'
            '        "guardrail": "must cite sources; refuse if no sources",'
        )
        return self._proposal(
            fix_type=FixType.GUARDRAIL_FIX,
            title="Require citations and refuse unsupported summary claims",
            rationale=(
                "Add a hard guardrail requiring citations for every summary claim and explicit "
                "refusal behavior when source support is missing."
            ),
            changes=[self._change(file_path, "add_output_guardrail", before, after)],
        )

    def _prompt_ambiguity_fix(self) -> FixProposal:
        file_path = "src/subjects/search_agent.py"
        before = (
            '            "instruction": "Find something useful and summarize it quickly.",\n'
            '            "ambiguity": "No concrete source material provided.",'
        )
        after = (
            '            "instruction": "Collect exactly 3 NYC to LAX options and summarize date, carrier, and price.",\n'
            '            "constraints": "If travel dates are missing, ask a clarifying question before using tools.",\n'
            '            "example": "User: Need flights soon. Assistant: Which departure date should I search?",\n'
            '            "ambiguity": "No concrete source material provided.",'
        )
        return self._proposal(
            fix_type=FixType.PROMPT_FIX,
            title="Tighten ambiguous search prompt with constraints and examples",
            rationale=(
                "Replace vague instruction text with explicit constraints and a clarifying-question "
                "example to reduce prompt ambiguity."
            ),
            changes=[self._change(file_path, "tighten_prompt", before, after)],
        )

    def _context_overflow_fix(self) -> FixProposal:
        file_path = "src/subjects/search_agent.py"
        before = '            "ambiguity": "No concrete source material provided.",'
        after = (
            '            "ambiguity": "No concrete source material provided.",\n'
            '            "context_budget": {\n'
            '                "max_chars": 2000,\n'
            '                "strategy": "summarize_then_restate_constraints"\n'
            "            },"
        )
        return self._proposal(
            fix_type=FixType.TOOL_CONFIG_FIX,
            title="Add explicit context budget and truncation strategy",
            rationale=(
                "Cap prompt context length and define a summarize-then-restate strategy to prevent "
                "context overflow failures."
            ),
            changes=[self._change(file_path, "cap_context_input", before, after)],
        )

    def _reasoning_error_fix(self) -> FixProposal:
        file_path = "src/subjects/booking_agent.py"
        before = '            "request": "Book a flight from NYC to LAX on 15/02/2026",'
        after = (
            '            "request": "Book a flight from NYC to LAX on 15/02/2026. "\n'
            '            "Before deciding, list assumptions, verify against tool output, then answer.",'
        )
        return self._proposal(
            fix_type=FixType.PROMPT_FIX,
            title="Add deterministic reasoning scaffold and self-check",
            rationale=(
                "Inject an assumptions-and-verification scaffold so the agent must reason "
                "deterministically and cross-check conclusions with tool output."
            ),
            changes=[self._change(file_path, "add_reasoning_scaffold", before, after)],
        )

    def _coordination_failure_fix(self) -> FixProposal:
        file_path = "src/subjects/run_subjects.py"
        before = (
            "        payload = booking_scenario_payload()\n"
            "        try:\n"
            "            return run_booking_scenario()"
        )
        after = (
            "        payload = booking_scenario_payload()\n"
            '        if "handoff_state" not in payload:\n'
            "            return {\n"
            '                "subject": subject,\n'
            '                "status": "failed",\n'
            '                "error": {"message": "missing handoff_state bundle"},\n'
            "            }\n"
            "        try:\n"
            "            return run_booking_scenario()"
        )
        return self._proposal(
            fix_type=FixType.GUARDRAIL_FIX,
            title="Validate handoff state bundle before delegation",
            rationale=(
                "Enforce a handoff protocol by requiring an explicit state bundle before delegated "
                "work continues."
            ),
            changes=[self._change(file_path, "validate_handoff_state", before, after)],
        )

    def _proposal(
        self,
        *,
        fix_type: FixType,
        title: str,
        rationale: str,
        changes: list[FixChange],
    ) -> FixProposal:
        return FixProposal(
            fix_type=fix_type,
            title=title,
            rationale=rationale,
            changes=changes,
        )

    def _change(self, file_path: str, change_type: str, before: str, after: str) -> FixChange:
        return FixChange(
            file=file_path,
            change_type=change_type,
            before=before,
            after=after,
            diff=unified_diff(before, after, file_path=file_path),
        )


def generate_fixes(
    diagnosis: Diagnosis | dict[str, object],
    findings_report: FindingsReport | dict[str, object],
) -> list[FixProposal]:
    return FixGenerator().generate_fixes(diagnosis, findings_report)
