# FaultAtlas Demo Scenario (2 minutes)

## Goal

Show one complete BookingAgent failure-to-fix loop in 2 minutes:

1. Failure is detected from DD/MM/YYYY input.
2. Analyzer findings explain what failed.
3. Diagnosis classifies root cause.
4. Fix generator shows concrete diff.

## Recording Setup (off-camera)

Use the project virtualenv so imports are stable:

```bash
.venv/bin/python demo/run_demo.py --mode live --store memory
```

If you need a guaranteed fallback output, use:

```bash
.venv/bin/python demo/run_demo.py --mode mock
```

## Timeline and Script

| Time | Narration (say this) | On-screen action | Highlight |
| --- | --- | --- | --- |
| 0:00-0:15 | "AI agents fail in production, but debugging them is slow and manual. FaultAtlas automates that autopsy flow." | Show terminal at repo root and `demo/scenario.md` briefly, then clear screen. | Frame the problem and promise the flow. |
| 0:15-0:30 | "I will run one command that reproduces a BookingAgent failure from a user date in DD/MM/YYYY format." | Run: `.venv/bin/python demo/run_demo.py --mode live --store memory` | One-command demo, no Azure dependency. |
| 0:30-0:45 | "Here is the failure event. The exact input is `15/02/2026`, which is invalid for the flight tool schema." | In output, focus the `failure_event` section and `date: \"15/02/2026\"` in payload metadata. | Failure detected + exact bad input. |
| 0:45-1:05 | "Next, the analyzers show where and why it failed: trace points to the failure step, and tool analysis shows schema mismatch on `date`." | Scroll to `findings.trace_analyzer` then `findings.tool_analyzer`. | Analyzer findings are explicit and structured. |
| 1:05-1:25 | "Diagnosis classifies this as `TOOL_MISUSE` with a confidence score, and explains the missing date transformation." | Scroll to `diagnosis`. Pause on `root_cause`, `confidence`, and `explanation`. | Root cause and explanation are machine-readable. |
| 1:25-1:45 | "Now FaultAtlas proposes a concrete fix and shows the exact diff to apply in the BookingAgent." | Scroll to `fixes[0].changes[0].diff`. | Human-reviewable fix diff, not vague advice. |
| 1:45-2:00 | "That is failure to analysis to diagnosis to fix proposal in one pass. If Azure is unavailable, the same story runs with mock fixtures." | Optionally run: `.venv/bin/python demo/run_demo.py --mode mock` and show equivalent sections. | Reliable fallback mode for live demo recording. |

## What must be visible in the terminal output

- `failure_event` (with BookingAgent failure type and timestamp)
- `findings.trace_analyzer` (failure step and reasoning chain)
- `findings.tool_analyzer` (schema mismatch for date)
- `diagnosis` (`TOOL_MISUSE`, confidence, explanation)
- `fixes` with a unified diff
