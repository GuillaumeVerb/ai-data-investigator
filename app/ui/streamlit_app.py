from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

from app.core.config import get_settings


st.set_page_config(
    page_title="AI Data Investigator",
    page_icon="AI",
    layout="wide",
)


API_BASE_URL = get_settings().api_base_url.rstrip("/")
SAMPLE_FILE = Path(__file__).resolve().parents[2] / "data" / "sample_sales.csv"


def api_post(path: str, json: dict | None = None, files: dict | None = None) -> dict:
    response = requests.post(f"{API_BASE_URL}{path}", json=json, files=files, timeout=60)
    response.raise_for_status()
    return response.json()


def reset_downstream_state() -> None:
    for key in ["profile", "investigation", "training", "simulation", "summary", "uploaded_file_name"]:
        st.session_state.pop(key, None)


def bootstrap_sample() -> None:
    if "dataset" not in st.session_state:
        st.session_state.dataset = api_post("/upload/sample")


bootstrap_sample()

st.title("AI Data Investigator")
st.caption("Upload data. Discover insights. Predict outcomes. Simulate scenarios.")

st.markdown(
    """
This MVP is built for a fast, business-facing demo:
`upload -> diagnostic -> investigation -> prediction -> simulation -> synthesis`
"""
)

left, right = st.columns([1.1, 0.9])
with left:
    uploaded_file = st.file_uploader("Upload a CSV", type=["csv"])
with right:
    st.write("Or keep using the built-in e-commerce sample dataset.")
    if st.button("Reload sample dataset", use_container_width=True):
        reset_downstream_state()
        st.session_state.dataset = api_post("/upload/sample")

if uploaded_file is not None and st.session_state.get("uploaded_file_name") != uploaded_file.name:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
    reset_downstream_state()
    st.session_state.dataset = api_post("/upload", files=files)
    st.session_state.uploaded_file_name = uploaded_file.name

dataset = st.session_state.dataset
dataset_id = dataset["dataset_id"]

tabs = st.tabs(
    [
        "1. Upload",
        "2. Diagnostic",
        "3. Investigation",
        "4. Prediction",
        "5. Simulation",
        "6. Summary",
    ]
)

with tabs[0]:
    st.subheader("Dataset Preview")
    st.write(f"File: `{dataset['filename']}`")
    st.write(f"Rows: `{dataset['rows']}` | Columns: `{dataset['columns']}`")
    st.dataframe(pd.DataFrame(dataset["preview"]), use_container_width=True)

with tabs[1]:
    profile = api_post("/profile", json={"dataset_id": dataset_id})
    st.session_state.profile = profile
    metric_cols = st.columns(3)
    metric_cols[0].metric("Rows", profile["shape"]["rows"])
    metric_cols[1].metric("Columns", profile["shape"]["columns"])
    metric_cols[2].metric("Quality Score", profile["quality_score"])
    st.write("Headline findings")
    for item in profile["headline_findings"]:
        st.write(f"- {item}")
    st.write("Target candidates")
    st.write(", ".join(profile["target_candidates"]) or "No obvious target candidates detected.")
    st.dataframe(
        pd.DataFrame(
            {
                "column": profile["columns"],
                "dtype": [profile["dtypes"][col] for col in profile["columns"]],
                "missing_pct": [profile["missing_pct"][col] for col in profile["columns"]],
            }
        ),
        use_container_width=True,
    )

with tabs[2]:
    investigation = api_post("/investigate", json={"dataset_id": dataset_id})
    st.session_state.investigation = investigation
    st.subheader("Top Insights")
    for insight in investigation["insights"]:
        st.markdown(
            f"**{insight['title']}**  \n{insight['description']}  \nSeverity: `{insight['severity']}` | Confidence: `{insight['confidence']}`"
        )
    st.subheader("Detected anomalies")
    if investigation["anomalies"]:
        st.dataframe(pd.DataFrame(investigation["anomalies"]), use_container_width=True)
    else:
        st.info("No strong anomalies detected with the current heuristic.")
    st.subheader("Automatic charts")
    for chart_spec in investigation["chart_specs"]:
        st.plotly_chart(go.Figure(chart_spec), use_container_width=True)

with tabs[3]:
    profile = st.session_state.get("profile") or api_post("/profile", json={"dataset_id": dataset_id})
    target_candidates = profile["target_candidates"] or profile["columns"]
    selected_target = st.selectbox("Select a business target", target_candidates)
    if st.button("Train baseline model", type="primary"):
        st.session_state.training = api_post(
            "/train", json={"dataset_id": dataset_id, "target": selected_target}
        )
    training = st.session_state.get("training")
    if training:
        metrics_col1, metrics_col2 = st.columns(2)
        metrics_col1.write(f"Model: `{training['model_name']}`")
        metrics_col1.json(training["metrics"])
        metrics_col2.write("Baseline metrics")
        metrics_col2.json(training["baseline_metrics"])
        st.subheader("Feature importance")
        st.dataframe(pd.DataFrame(training["feature_importance"]), use_container_width=True)

with tabs[4]:
    training = st.session_state.get("training")
    if not training:
        st.info("Train a model in the Prediction tab to unlock simulation.")
    else:
        reference = training["reference_row"]
        numeric_reference = {k: v for k, v in reference.items() if isinstance(v, (int, float))}
        categorical_reference = {k: v for k, v in reference.items() if not isinstance(v, (int, float))}
        changes: dict[str, object] = {}

        st.subheader("What-if controls")
        for column, value in list(numeric_reference.items())[:3]:
            changes[column] = st.number_input(
                f"{column}",
                value=float(value),
            )
        for column, value in list(categorical_reference.items())[:2]:
            changes[column] = st.text_input(f"{column}", value=str(value))

        if st.button("Run simulation", type="primary"):
            st.session_state.simulation = api_post(
                "/simulate",
                json={
                    "dataset_id": dataset_id,
                    "model_id": training["model_id"],
                    "changes": changes,
                },
            )
        simulation = st.session_state.get("simulation")
        if simulation:
            col1, col2, col3 = st.columns(3)
            col1.metric("Before", simulation["prediction_before"])
            col2.metric("After", simulation["prediction_after"])
            col3.metric("Delta %", simulation["delta_pct"] if simulation["delta_pct"] is not None else "N/A")
            st.write(simulation["narrative"])
            st.write("Reference row")
            st.json(simulation["reference_row"])
            st.write("Simulated row")
            st.json(simulation["simulated_row"])

with tabs[5]:
    if st.button("Generate executive summary", type="primary"):
        payload = {
            "dataset_id": dataset_id,
            "profile": st.session_state.get("profile") or api_post("/profile", json={"dataset_id": dataset_id}),
            "investigation": st.session_state.get("investigation")
            or api_post("/investigate", json={"dataset_id": dataset_id}),
            "training": st.session_state.get("training"),
            "simulation": st.session_state.get("simulation"),
        }
        st.session_state.summary = api_post("/summary", json=payload)

    summary = st.session_state.get("summary")
    if summary:
        st.subheader("Executive Summary")
        st.write(summary["executive_summary"])
        st.write("Recommendations")
        for item in summary["recommendations"]:
            st.write(f"- {item}")
        st.write("Limitations")
        for item in summary["limitations"]:
            st.write(f"- {item}")

st.warning(
    "Guardrails: this MVP surfaces statistical patterns and model-based simulations. It does not provide causal proof."
)
