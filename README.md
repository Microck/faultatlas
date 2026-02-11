# FaultAtlas

FaultAtlas is a meta-agent system that debugs other AI agents when they fail: it captures a failure event, analyzes trace and tool behavior, diagnoses root cause with a shared taxonomy, and proposes concrete fixes. For a hackathon demo, this matters because judges can see a full failure-to-fix workflow in one pass instead of reading raw traces manually.

## Architecture (DEMO-04 Agent Definition)

In this project, an **agent** is a distinct role/module invoked in the autopsy pipeline.

The 8 agents shown in DEMO-04 are:
- `BookingAgent`
- `SearchAgent`
- `SummaryAgent`
- `FailureDetector`
- `TraceAnalyzer`
- `ToolAnalyzer`
- `DiagnosisEngine`
- `FixGenerator`

`AutopsyController` and `AutopsyPipeline` are orchestration glue (shown in the diagram), not counted as separate agents.

- Diagram: `docs/architecture.png`
- Diagram source (Mermaid): `docs/architecture.mmd`
- Failure taxonomy: `docs/failure_taxonomy.md`

If `docs/architecture.png` is missing in a headless environment, render it locally with:

```bash
npx -y @mermaid-js/mermaid-cli -i docs/architecture.mmd -o docs/architecture.png
```

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables (create your local `.env` from `.env.example`):
- Foundry runtime:
  - `FOUNDRY_PROJECT_ENDPOINT`
  - `FOUNDRY_MODEL_DEPLOYMENT`
  - `APPLICATIONINSIGHTS_CONNECTION_STRING` (optional)
- Optional Cosmos backends for trace/fix history:
  - `COSMOS_ENDPOINT`
  - `COSMOS_KEY`
  - `COSMOS_DATABASE`
  - `COSMOS_CONTAINER_TRACES`
  - `COSMOS_CONTAINER_FIXES`

## Usage

Run deterministic subject failure scenarios:

```bash
python -m src.subjects.run_subjects booking
python -m src.subjects.run_subjects search
python -m src.subjects.run_subjects summary
```

Run the demo output flow (mock mode):

```bash
python demo/run_demo.py --mode mock
```

## Demo Assets

- Scenario script: `demo/scenario.md`
- Architecture diagram: `docs/architecture.png`
- Failure taxonomy: `docs/failure_taxonomy.md`
