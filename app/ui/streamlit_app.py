from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import get_settings


st.set_page_config(
    page_title="AI Data Investigator",
    page_icon="AI",
    layout="wide",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    :root {
        --sand: #f6f0e8;
        --ink: #1f2620;
        --forest: #123524;
        --moss: #306844;
        --amber: #d78332;
        --rose: #f2dfd9;
        --panel: rgba(255, 252, 247, 0.82);
        --line: rgba(18, 53, 36, 0.12);
    }
    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(215, 131, 50, 0.12), transparent 28%),
            radial-gradient(circle at top right, rgba(48, 104, 68, 0.16), transparent 32%),
            linear-gradient(180deg, #f9f5ef 0%, #f0e7db 100%);
        color: var(--ink);
        font-family: 'Space Grotesk', sans-serif;
    }
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }
    [data-testid="stSidebar"] {
        background: rgba(255, 250, 244, 0.9);
        border-right: 1px solid var(--line);
    }
    .hero-card, .panel-card, .metric-card, .insight-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 22px;
        box-shadow: 0 18px 60px rgba(34, 31, 25, 0.08);
    }
    .hero-card {
        padding: 2rem 2.2rem;
        margin-bottom: 1rem;
    }
    .hero-kicker {
        color: var(--moss);
        font-size: 0.82rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        font-family: 'IBM Plex Mono', monospace;
    }
    .hero-title {
        font-size: 3rem;
        line-height: 0.95;
        color: var(--forest);
        margin: 0.45rem 0 0.9rem 0;
    }
    .hero-copy {
        font-size: 1.05rem;
        line-height: 1.55;
        max-width: 58rem;
    }
    .hero-flow {
        margin-top: 1rem;
        font-family: 'IBM Plex Mono', monospace;
        color: var(--amber);
        font-size: 0.9rem;
    }
    .panel-card {
        padding: 1.2rem 1.25rem;
        margin-bottom: 1rem;
    }
    .panel-title {
        color: var(--forest);
        font-size: 1.15rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        padding: 1rem 1.1rem;
        min-height: 118px;
    }
    .metric-label {
        color: rgba(31, 38, 32, 0.72);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-family: 'IBM Plex Mono', monospace;
    }
    .metric-value {
        color: var(--forest);
        font-size: 2rem;
        margin-top: 0.3rem;
        font-weight: 700;
    }
    .metric-foot {
        color: rgba(31, 38, 32, 0.76);
        font-size: 0.92rem;
        margin-top: 0.4rem;
    }
    .insight-card {
        padding: 1rem 1.1rem;
        margin-bottom: 0.8rem;
    }
    .insight-title {
        color: var(--forest);
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .insight-meta {
        font-family: 'IBM Plex Mono', monospace;
        color: rgba(31, 38, 32, 0.7);
        font-size: 0.82rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.35rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 252, 247, 0.8);
        border-radius: 999px;
        padding: 0.55rem 0.95rem;
        border: 1px solid var(--line);
    }
</style>
""",
    unsafe_allow_html=True,
)


API_BASE_URL = get_settings().api_base_url.rstrip("/")


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


def render_metric_card(label: str, value: str, foot: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="panel-card">
            <div class="panel-title">{title}</div>
            <div>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


bootstrap_sample()
dataset = st.session_state.dataset
dataset_id = dataset["dataset_id"]

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-kicker">AI Data Investigator</div>
        <div class="hero-title">Your dataset, investigated like a business case.</div>
        <div class="hero-copy">
            This experience blends data profiling, automatic investigation, predictive modeling,
            what-if simulation, and executive-ready storytelling. The goal is not only to inspect data,
            but to explain what matters and what decision-makers should look at next.
        </div>
        <div class="hero-flow">upload -> diagnose -> investigate -> predict -> simulate -> brief</div>
    </div>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([1.1, 0.9], vertical_alignment="center")
with top_left:
    uploaded_file = st.file_uploader("Upload a CSV", type=["csv"], label_visibility="visible")
with top_right:
    st.markdown("**Demo dataset**")
    st.write("The built-in sample is tuned for e-commerce, revenue, pricing, and churn-style exploration.")
    if st.button("Reload demo dataset", use_container_width=True):
        reset_downstream_state()
        st.session_state.dataset = api_post("/upload/sample")

if uploaded_file is not None and st.session_state.get("uploaded_file_name") != uploaded_file.name:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
    reset_downstream_state()
    st.session_state.dataset = api_post("/upload", files=files)
    st.session_state.uploaded_file_name = uploaded_file.name
    dataset = st.session_state.dataset
    dataset_id = dataset["dataset_id"]

profile = st.session_state.get("profile") or api_post("/profile", json={"dataset_id": dataset_id})
st.session_state.profile = profile
investigation = st.session_state.get("investigation") or api_post("/investigate", json={"dataset_id": dataset_id})
st.session_state.investigation = investigation

metric_cols = st.columns(4)
with metric_cols[0]:
    render_metric_card("Rows", str(profile["shape"]["rows"]), "Records ready for analysis")
with metric_cols[1]:
    render_metric_card("Columns", str(profile["shape"]["columns"]), "Usable business signals detected")
with metric_cols[2]:
    render_metric_card("Quality Score", str(profile["quality_score"]), "Simple health score before modeling")
with metric_cols[3]:
    render_metric_card("Insights", str(len(investigation["insights"])), "Prioritized patterns surfaced automatically")

executive_cols = st.columns([1.25, 0.75], vertical_alignment="top")
with executive_cols[0]:
    render_panel("Executive Brief", investigation["executive_brief"])
with executive_cols[1]:
    render_panel(
        "AI Guardrail",
        "This product surfaces statistical evidence and model-based scenarios. It helps frame decisions, but it does not prove causality.",
    )

tabs = st.tabs(
    [
        "Upload",
        "Diagnostic",
        "Investigation",
        "Prediction",
        "Simulation",
        "Executive Summary",
    ]
)

with tabs[0]:
    st.subheader("Dataset Preview")
    render_panel(
        "Session Context",
        f"Current file: <strong>{dataset['filename']}</strong><br>Rows: {dataset['rows']}<br>Columns: {dataset['columns']}",
    )
    st.dataframe(pd.DataFrame(dataset["preview"]), use_container_width=True, hide_index=True)

with tabs[1]:
    st.subheader("Diagnostic")
    left, right = st.columns([0.9, 1.1], vertical_alignment="top")
    with left:
        render_panel("Headline Findings", "<br>".join(profile["headline_findings"]))
        targets = ", ".join(profile["target_candidates"]) or "No obvious target candidates detected yet."
        render_panel("Suggested Targets", targets)
    with right:
        profile_df = pd.DataFrame(
            {
                "column": profile["columns"],
                "dtype": [profile["dtypes"][col] for col in profile["columns"]],
                "missing_pct": [profile["missing_pct"][col] for col in profile["columns"]],
            }
        )
        st.dataframe(profile_df, use_container_width=True, hide_index=True)

with tabs[2]:
    st.subheader("AI Investigation")
    st.markdown("**Priority insights**")
    for insight in investigation["insights"]:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">{insight['title']}</div>
                <div>{insight['description']}</div>
                <div class="insight-meta">severity={insight['severity']} | confidence={insight['confidence']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    brief_cols = st.columns(2, vertical_alignment="top")
    with brief_cols[0]:
        render_panel("Anomaly Narrative", investigation["anomaly_narrative"])
    with brief_cols[1]:
        render_panel("Opportunity Areas", "<br>".join(f"- {item}" for item in investigation["opportunity_areas"]))

    st.markdown("**Detected anomalies**")
    if investigation["anomalies"]:
        st.dataframe(pd.DataFrame(investigation["anomalies"]), use_container_width=True, hide_index=True)
    else:
        st.info("No strong anomalies detected with the current heuristic.")

    st.markdown("**Automatic charts**")
    for chart_spec in investigation["chart_specs"]:
        st.plotly_chart(go.Figure(chart_spec), use_container_width=True)

with tabs[3]:
    st.subheader("Prediction Engine")
    target_candidates = profile["target_candidates"] or profile["columns"]
    selected_target = st.selectbox("Choose a business target", target_candidates)
    if st.button("Train baseline model", type="primary"):
        st.session_state.training = api_post("/train", json={"dataset_id": dataset_id, "target": selected_target})

    training = st.session_state.get("training")
    if training:
        left, right = st.columns([0.8, 1.2], vertical_alignment="top")
        with left:
            render_panel(
                "Model Snapshot",
                f"Model: <strong>{training['model_name']}</strong><br>Target: <strong>{training['target']}</strong><br>Task: <strong>{training['task_type']}</strong>",
            )
            st.json(training["metrics"])
            st.caption("Baseline comparison")
            st.json(training["baseline_metrics"])
        with right:
            st.markdown("**Feature Importance**")
            st.dataframe(pd.DataFrame(training["feature_importance"]), use_container_width=True, hide_index=True)
    else:
        st.info("Train a baseline model to unlock simulation and the executive summary.")

with tabs[4]:
    st.subheader("Scenario Simulation")
    training = st.session_state.get("training")
    if not training:
        st.info("Train a model in the Prediction tab to unlock simulation.")
    else:
        reference = training["reference_row"]
        numeric_reference = {k: v for k, v in reference.items() if isinstance(v, (int, float))}
        categorical_reference = {k: v for k, v in reference.items() if not isinstance(v, (int, float))}
        changes: dict[str, object] = {}

        control_cols = st.columns(2, vertical_alignment="top")
        with control_cols[0]:
            st.markdown("**Numeric levers**")
            for column, value in list(numeric_reference.items())[:3]:
                changes[column] = st.number_input(column, value=float(value))
        with control_cols[1]:
            st.markdown("**Categorical levers**")
            for column, value in list(categorical_reference.items())[:2]:
                changes[column] = st.text_input(column, value=str(value))

        if st.button("Run AI scenario brief", type="primary"):
            st.session_state.simulation = api_post(
                "/simulate",
                json={"dataset_id": dataset_id, "model_id": training["model_id"], "changes": changes},
            )

        simulation = st.session_state.get("simulation")
        if simulation:
            sim_cols = st.columns(3)
            sim_cols[0].metric("Before", simulation["prediction_before"])
            sim_cols[1].metric("After", simulation["prediction_after"])
            sim_cols[2].metric("Delta %", simulation["delta_pct"] if simulation["delta_pct"] is not None else "N/A")
            render_panel("AI Simulation Narrative", simulation["narrative"])
            render_panel("Business Impact", simulation["impact_summary"])
            render_panel("Guardrail", simulation["guardrail_note"])

with tabs[5]:
    st.subheader("Executive Summary")
    if st.button("Generate board-ready brief", type="primary"):
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
        render_panel(summary["headline"], summary["executive_summary"])
        left, right = st.columns(2, vertical_alignment="top")
        with left:
            render_panel("Recommendations", "<br>".join(f"- {item}" for item in summary["recommendations"]))
        with right:
            render_panel("Limitations", "<br>".join(f"- {item}" for item in summary["limitations"]))
    else:
        st.info("Generate the board-ready brief to see the final AI narrative.")

st.caption(
    "This phase 2 experience makes the AI layer more visible by adding executive narration to investigation, simulation, and summary."
)
