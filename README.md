# AI Decision Copilot

AI Decision Copilot is a premium analytics product that turns a dataset into an investigation, prediction, simulation, and reporting workflow:

`upload -> diagnose -> investigate -> explain -> simulate -> recommend -> export`

It is designed for:

- portfolio and freelance positioning
- short product demos
- business-facing AI storytelling
- future SaaS evolution

## Product Positioning

This is not just a "chat with CSV" app. It behaves like an AI business analyst that can:

- profile and score insights automatically
- suggest investigation paths
- train explainable predictive models
- compare scenarios before decisions
- surface root-cause hypotheses
- recommend business actions
- export a consulting-style HTML report

## Core Capabilities

- CSV upload and sample dataset
- automatic profiling and derived features
- ranked investigation suggestions
- root-cause analysis
- prediction engine with explainability
- scenario comparison
- enrichment suggestions
- multi-dataset merge preview
- memory-enabled decision copilot
- executive report export in HTML

## Architecture

```text
User -> Streamlit UI -> FastAPI API
                      -> ingestion
                      -> profiling
                      -> investigation_agent
                      -> root_cause
                      -> ml_engine
                      -> scenario_engine
                      -> action_engine
                      -> enrichment_agent
                      -> copilot_agent
                      -> report_export
```

## Quick Demo Flow

1. Load the sample dataset.
2. Review investigation suggestions.
3. Train the prediction engine on `revenue`.
4. Compare scenario A vs B.
5. Ask the Decision Copilot a business question.
6. Export the HTML executive report.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.api.main:app --reload
streamlit run app/ui/streamlit_app.py
```

## Real LLM Setup

The copilot can use OpenAI for:

- executive summaries
- copilot answers
- business narration for investigation and simulation

Configure:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
AUTO_START_LOCAL_API=true
API_BASE_URL=http://127.0.0.1:8000
```

If `OPENAI_API_KEY` is missing, the app stays functional and falls back to deterministic narrative templates.

## Streamlit Deployment

For a simple portfolio deployment, use Streamlit and point the app entry file to:

```text
streamlit_app.py
```

This repo now includes:

- a root Streamlit entrypoint
- `.streamlit/config.toml`
- auto-start of the local FastAPI backend when `API_BASE_URL` targets `127.0.0.1` or `localhost`

Recommended Streamlit secrets or environment variables:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
AUTO_START_LOCAL_API=true
API_BASE_URL=http://127.0.0.1:8000
```

Recommended deployment path:

1. Deploy the Streamlit app first for demo speed.
2. Keep `AUTO_START_LOCAL_API=true` for a single-service setup.
3. Move the API to a separate service later if you need stronger scale, uptime, or enterprise isolation.

## Key API Endpoints

- `POST /upload`
- `POST /upload/sample`
- `GET /datasets`
- `POST /profile`
- `POST /investigate`
- `POST /investigate-path`
- `POST /root-cause`
- `POST /train`
- `POST /simulate`
- `POST /actions`
- `POST /enrichment-suggestions`
- `POST /merge-preview`
- `POST /copilot/ask`
- `GET /copilot/session/{session_id}`
- `POST /copilot/session/{session_id}/reset`
- `POST /summary`
- `POST /report/export`

## Screenshots To Capture

- landing hero
- investigation suggestions
- prediction engine with top drivers
- scenario comparison
- copilot reasoning panel
- exported executive report

## Guardrails

- Outputs are based on statistical patterns and model behavior.
- Simulations are directional guidance, not causal evidence.
- Confidence depends on model quality and data coverage.

## Next Product Steps

- richer copilot planning and memory
- persistent run history
- SQL connectors and merged analysis
- PDF export after HTML validation
- templates for pricing, churn, and revenue use cases
