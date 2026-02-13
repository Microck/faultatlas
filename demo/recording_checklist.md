# Recording Checklist (DEMO-02)

## Recording Goal

- Capture a ~2:00 demo video that follows `demo/scenario.md`.
- Show the complete flow: failure detected -> findings -> diagnosis -> fix diff.
- Recording is a manual step later; this checklist keeps it repeatable.

## Pre-Flight Checks

- [ ] Mic input is active and narration is clear.
- [ ] System audio is disabled or balanced so voice-over stays clear.
- [ ] Terminal font is readable at video resolution (increase before recording if needed).
- [ ] Terminal window is sized wide enough to avoid wrapped JSON keys.
- [ ] Start from repository root: `.`
- [ ] Keep fallback command ready: `.venv/bin/python demo/run_demo.py --mode mock`.

## Commands to Run (In Order)

1. Confirm location:

```bash
pwd
```

2. Optional provenance marker in terminal:

```bash
git rev-parse --short HEAD
```

3. Clear terminal before narration starts:

```bash
clear
```

4. Run the live demo path used in the script:

```bash
.venv/bin/python demo/run_demo.py --mode live --store memory
```

5. If live mode cannot run in recording environment, switch immediately to fallback:

```bash
.venv/bin/python demo/run_demo.py --mode mock
```

## Visual Callouts to Capture

- [ ] **Failure detected:** `failure_event` block and invalid date (`15/02/2026`).
- [ ] **Findings:** `findings.trace_analyzer` and `findings.tool_analyzer` sections.
- [ ] **Diagnosis:** `diagnosis.root_cause`, `diagnosis.confidence`, and `diagnosis.explanation`.
- [ ] **Diff:** `fixes[0].changes[0].diff` showing concrete fix output.

## Export Requirements

- [ ] Export format: MP4.
- [ ] Target runtime: about 2:00.
- [ ] Final file path: `demo/video.mp4`.
- [ ] Playback check before submit: readable terminal text and clear audio.
