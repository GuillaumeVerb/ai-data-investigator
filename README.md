# AI Data Investigator

AI Data Investigator is a demo-first analytics agent that turns a flat dataset into a business-facing workflow:

`upload -> diagnostic -> investigation -> prediction -> simulation -> synthesis`

It is designed to work well as:

- a strong portfolio project
- a Malt/freelance showcase
- a foundation for a future analytics SaaS

## Why This Project

This MVP goes beyond a simple "chat with your CSV" experience. It:

- profiles a dataset automatically
- highlights patterns and anomalies without waiting for a prompt
- trains a baseline predictive model on a chosen business target
- simulates what-if scenarios
- generates an executive-ready summary with guardrails

## Stack

- UI: Streamlit
- API: FastAPI + Pydantic
- Analysis: pandas + numpy
- ML: scikit-learn
- Visuals: Plotly
- Narrative layer: OpenAI with a safe fallback summary

## Architecture

```text
User -> Streamlit UI -> FastAPI API
                      -> ingestion
                      -> profiling
                      -> insights
                      -> ml_engine
                      -> scenario_engine
                      -> llm_engine
```

## Features

- CSV upload and built-in demo dataset
- automatic data profiling and target suggestions
- 3 to 5 generated insights
- simple anomaly detection
- automatic charts
- baseline model training for regression or classification
- feature importance
- what-if simulation
- executive summary with recommendations and limitations

## Quickstart

1. Create a virtual environment and install dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy the environment template and optionally add an OpenAI API key.

```bash
cp .env.example .env
```

3. Start the API.

```bash
uvicorn app.api.main:app --reload
```

4. In another terminal, start the UI.

```bash
streamlit run app/ui/streamlit_app.py
```

## Demo Dataset

The repo ships with [`data/sample_sales.csv`](/Users/guillaumeverbiguie/Desktop/AI Data Investigator/data/sample_sales.csv), a compact e-commerce dataset with:

- product, region, channel, and segment dimensions
- pricing and marketing inputs
- revenue and churn-oriented targets

## API Endpoints

- `POST /upload`
- `POST /upload/sample`
- `POST /profile`
- `POST /investigate`
- `POST /train`
- `POST /simulate`
- `POST /summary`

## Guardrails

- Insights are statistical signals, not business truth by default.
- Simulation reflects model behavior on observed data, not causal proof.
- The MVP optimizes for clarity and explainability over advanced model complexity.

## Portfolio Angle

The project is intentionally polished for short demos:

- clear user journey in six screens
- visible business framing
- readable metrics and simulation output
- executive summary that a decision-maker can understand quickly

## Next Steps

- SQL connectors
- model comparison
- exportable PDF/HTML reports
- run history
- domain templates for churn, pricing, revenue, and marketing
