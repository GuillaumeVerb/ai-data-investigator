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
User -> Web frontend served by FastAPI
     -> FastAPI API
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

The FastAPI app now serves a lightweight web frontend at `/`, so the Railway deployment can expose both:

- the API endpoints
- the portfolio/demo interface

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

## Render Deployment For The API

For a more stable deployment, deploy the FastAPI backend separately on Render.

This repo now includes:

- [render.yaml](/Users/guillaumeverbiguie/Desktop/AI%20Data%20Investigator/render.yaml)
- [Procfile](/Users/guillaumeverbiguie/Desktop/AI%20Data%20Investigator/Procfile)

Recommended Render setup:

1. Create a new Web Service from this repo.
2. Use the Blueprint from `render.yaml` or configure manually.
3. Start command:

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port $PORT
```

4. Health check path:

```text
/health
```

5. Required environment variables:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
APP_NAME=AI Data Investigator
ANOMALY_CONTAMINATION=0.08
MAX_PREVIEW_ROWS=10
```

Once the backend is live, point the frontend to the public API:

```bash
API_BASE_URL=https://your-render-service.onrender.com
AUTO_START_LOCAL_API=false
```

Recommended architecture:

1. Deploy FastAPI on Render.
2. Keep Streamlit only as the UI layer.
3. Update the Streamlit secrets to use the public Render API URL.

This is the fastest path to a more reliable online demo without rewriting the frontend.

## Railway Deployment For The API

If you want a simpler backend deployment than Render, Railway is a good fit for this project.

This repo now includes:

- [railway.json](/Users/guillaumeverbiguie/Desktop/AI%20Data%20Investigator/railway.json)
- [.python-version](/Users/guillaumeverbiguie/Desktop/AI%20Data%20Investigator/.python-version)

Recommended Railway setup:

1. Create a new project from the GitHub repo.
2. Let Railway detect the repo with Nixpacks.
3. The backend start command is already defined as:

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port $PORT
```

4. Add these environment variables:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
APP_NAME=AI Data Investigator
ANOMALY_CONTAMINATION=0.08
MAX_PREVIEW_ROWS=10
```

5. Once deployed, test:

```text
https://your-railway-service.up.railway.app/health
```

Then point the frontend to the public API:

```bash
API_BASE_URL=https://your-railway-service.up.railway.app
AUTO_START_LOCAL_API=false
```

Recommended flow:

1. Deploy the FastAPI backend on Railway.
2. Verify `/health` returns `status: ok`.
3. Update the Streamlit frontend secrets with the Railway URL.

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
