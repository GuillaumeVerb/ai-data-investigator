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


st.set_page_config(page_title="AI Data Investigator", page_icon="AI", layout="wide")

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    :root {
        --cream: #f7f1e8;
        --forest: #163828;
        --moss: #2f6d49;
        --amber: #d38336;
        --danger: #b44747;
        --panel: rgba(255, 252, 247, 0.84);
        --line: rgba(22, 56, 40, 0.12);
    }
    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(211, 131, 54, 0.14), transparent 26%),
            radial-gradient(circle at top right, rgba(47, 109, 73, 0.18), transparent 30%),
            linear-gradient(180deg, #faf6f0 0%, #f1e8da 100%);
        color: #1d241f;
        font-family: 'Space Grotesk', sans-serif;
    }
    [data-testid="stHeader"] { background: transparent; }
    .hero, .card, .metric-card, .insight-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 24px;
        box-shadow: 0 20px 50px rgba(30, 29, 23, 0.08);
    }
    .hero { padding: 2rem 2.2rem; margin-bottom: 1rem; }
    .hero-title { color: var(--forest); font-size: 3rem; line-height: .96; margin: .4rem 0 .7rem 0; }
    .hero-kicker, .meta { font-family: 'IBM Plex Mono', monospace; letter-spacing: .12em; text-transform: uppercase; font-size: .8rem; color: var(--moss); }
    .card { padding: 1.1rem 1.2rem; margin-bottom: 1rem; }
    .metric-card { padding: 1rem 1.1rem; min-height: 120px; }
    .metric-value { color: var(--forest); font-size: 1.9rem; font-weight: 700; }
    .insight-card { padding: 1rem 1.1rem; margin-bottom: .8rem; border-left: 8px solid var(--moss); }
    .insight-card.high { border-left-color: var(--danger); }
    .insight-card.medium { border-left-color: var(--amber); }
    .insight-card.low { border-left-color: var(--moss); }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,252,247,0.84);
        border-radius: 999px;
        border: 1px solid var(--line);
        padding: .55rem .95rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

API_BASE_URL = get_settings().api_base_url.rstrip("/")


def api_post(path: str, json: dict | None = None, files: dict | None = None) -> dict:
    response = requests.post(f"{API_BASE_URL}{path}", json=json, files=files, timeout=90)
    response.raise_for_status()
    return response.json()


def reset_downstream_state() -> None:
    for key in [
        "profile",
        "investigation",
        "training",
        "simulation",
        "summary",
        "actions",
        "focused_analysis",
        "uploaded_file_name",
    ]:
        st.session_state.pop(key, None)


def bootstrap_sample() -> None:
    if "dataset" not in st.session_state:
        st.session_state.dataset = api_post("/upload/sample")


def render_card(title: str, body: str) -> None:
    st.markdown(f'<div class="card"><div><strong>{title}</strong></div><div>{body}</div></div>', unsafe_allow_html=True)


def render_metric(label: str, value: str, foot: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="meta">{label}</div><div class="metric-value">{value}</div><div>{foot}</div></div>',
        unsafe_allow_html=True,
    )


def ensure_actions(dataset_id: str) -> dict:
    if "actions" not in st.session_state or not st.session_state.actions:
        st.session_state.actions = api_post(
            "/actions",
            json={
                "dataset_id": dataset_id,
                "investigation": st.session_state.investigation,
                "training": st.session_state.get("training"),
                "simulation": st.session_state.get("simulation"),
            },
        )
    return st.session_state.actions


bootstrap_sample()
dataset = st.session_state.dataset
dataset_id = dataset["dataset_id"]

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">AI Data Investigator</div>
        <div class="hero-title">Premium investigation for business datasets.</div>
        <div>
            Upload data, surface ranked insights, investigate promising paths, train a prediction engine,
            compare scenarios, and generate board-ready actions.
        </div>
        <div class="meta" style="margin-top:1rem;">upload -> diagnostic -> investigation -> prediction -> simulation -> executive summary</div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.05, 0.95], vertical_alignment="center")
with left:
    uploaded_file = st.file_uploader("Upload a CSV", type=["csv"])
with right:
    st.write("Use the built-in e-commerce sample to see the full flow instantly.")
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
profile = st.session_state.get("profile") or api_post("/profile", json={"dataset_id": dataset_id})
investigation = st.session_state.get("investigation") or api_post("/investigate", json={"dataset_id": dataset_id})
st.session_state.profile = profile
st.session_state.investigation = investigation

metric_cols = st.columns(4)
with metric_cols[0]:
    render_metric("Rows", str(profile["shape"]["rows"]), "Records available")
with metric_cols[1]:
    render_metric("Coverage", f"{profile['data_coverage_pct']}%", "Usable data completeness")
with metric_cols[2]:
    render_metric("Insights", str(len(investigation["insights"])), "Ranked by importance")
with metric_cols[3]:
    render_metric("Suggestions", str(len(investigation["investigation_suggestions"])), "Investigable AI paths")

header_cols = st.columns([1.15, 0.85], vertical_alignment="top")
with header_cols[0]:
    render_card("Executive Brief", investigation["executive_brief"])
with header_cols[1]:
    render_card("Guardrail", "This is based on model behavior and statistical evidence, not causal inference.")

tabs = st.tabs(
    [
        "Diagnostic",
        "Investigation Suggestions",
        "Insights",
        "Prediction",
        "Scenario Simulation",
        "Recommended Actions",
        "Executive Summary",
    ]
)

with tabs[0]:
    diag_cols = st.columns([0.9, 1.1], vertical_alignment="top")
    with diag_cols[0]:
        render_card("Headline Findings", "<br>".join(profile["headline_findings"]))
        render_card("Suggested Targets", ", ".join(profile["target_candidates"]) or "No obvious target.")
        render_card("Derived Features", "<br>".join(f"- {item}" for item in profile["derived_features"]) or "No derived features available.")
    with diag_cols[1]:
        st.dataframe(
            pd.DataFrame(
                {
                    "column": profile["columns"],
                    "dtype": [profile["dtypes"][col] for col in profile["columns"]],
                    "missing_pct": [profile["missing_pct"][col] for col in profile["columns"]],
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

with tabs[1]:
    st.subheader("Investigation Suggestions")
    for suggestion in investigation["investigation_suggestions"]:
        cols = st.columns([0.78, 0.22], vertical_alignment="center")
        with cols[0]:
            render_card(
                suggestion["title"],
                f"{suggestion['explanation']}<br><span class='meta'>priority {int(suggestion['priority_score'] * 100)}%</span>",
            )
        with cols[1]:
            if st.button(
                suggestion["button_label"],
                key=f"investigate_{suggestion['suggestion_id']}",
                use_container_width=True,
            ):
                payload = dict(suggestion["payload"])
                payload["investigation_type"] = suggestion["investigation_type"]
                st.session_state.focused_analysis = api_post(
                    "/investigate-path",
                    json={
                        "dataset_id": dataset_id,
                        "suggestion_id": suggestion["suggestion_id"],
                        "payload": payload,
                    },
                )

    focused = st.session_state.get("focused_analysis")
    if focused:
        st.markdown("### Deeper Analysis")
        render_card(focused["title"], f"{focused['analysis']}<br><br><strong>Business implication:</strong> {focused['business_implication']}")
        st.json(focused["supporting_stats"])
        if focused.get("chart_spec"):
            st.plotly_chart(go.Figure(focused["chart_spec"]), use_container_width=True)

with tabs[2]:
    st.subheader("Ranked Insights")
    for insight in investigation["insights"]:
        st.markdown(
            f"""
            <div class="insight-card {insight['impact_level']}">
                <div><strong>{insight['title']}</strong></div>
                <div>{insight['description']}</div>
                <div class="meta">{insight['icon']} | type={insight['insight_type']} | impact={insight['impact_level']} | confidence={insight['confidence_pct']}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    detail_cols = st.columns(2, vertical_alignment="top")
    with detail_cols[0]:
        render_card("Anomaly Narrative", investigation["anomaly_narrative"])
        if investigation["anomalies"]:
            st.dataframe(pd.DataFrame(investigation["anomalies"]), use_container_width=True, hide_index=True)
    with detail_cols[1]:
        render_card("Opportunity Areas", "<br>".join(f"- {item}" for item in investigation["opportunity_areas"]))
    for chart_spec in investigation["chart_specs"]:
        st.plotly_chart(go.Figure(chart_spec), use_container_width=True)

with tabs[3]:
    st.subheader("Prediction Engine")
    target_candidates = profile["target_candidates"] or profile["columns"]
    target = st.selectbox("Choose a target", target_candidates)
    if st.button("Train model", type="primary"):
        st.session_state.training = api_post("/train", json={"dataset_id": dataset_id, "target": target})
        st.session_state.actions = None

    training = st.session_state.get("training")
    if training:
        left, right = st.columns([0.85, 1.15], vertical_alignment="top")
        with left:
            render_card(
                "Model trained successfully",
                (
                    f"Model type: <strong>{training['task_type']}</strong><br>"
                    f"Model: <strong>{training['model_name']}</strong><br>"
                    f"{training['primary_metric_name'].upper()} = <strong>{training['primary_metric_value']}</strong><br>"
                    f"Confidence level: <strong>{training['confidence_level']}</strong><br>"
                    f"Data coverage: <strong>{training['data_coverage_pct']}%</strong>"
                ),
            )
            render_card(
                "Top drivers",
                "<br>".join(f"{idx + 1}. {driver}" for idx, driver in enumerate(training["top_drivers"][:5])),
            )
            st.caption("Baseline comparison")
            st.json(training["baseline_metrics"])
        with right:
            st.plotly_chart(go.Figure(training["feature_importance_chart"]), use_container_width=True)
            st.dataframe(pd.DataFrame(training["feature_importance"][:5]), use_container_width=True, hide_index=True)
    else:
        st.info("Train a model to unlock scenario simulation and stronger business actions.")

with tabs[4]:
    st.subheader("Scenario Simulation")
    training = st.session_state.get("training")
    if not training:
        st.info("Train a model first.")
    else:
        reference = training["reference_row"]
        slider_candidates = [col for col in ["price", "marketing_spend", "discount_pct"] if col in reference]
        scenario_cols = st.columns(2, vertical_alignment="top")
        scenario_a: dict[str, object] = {}
        scenario_b: dict[str, object] = {}

        with scenario_cols[0]:
            st.markdown("**Scenario A**")
            for column in slider_candidates:
                scenario_a[column] = st.slider(
                    f"A - {column}",
                    min_value=float(reference[column]) * 0.5,
                    max_value=float(reference[column]) * 1.5 + 1,
                    value=float(reference[column]),
                )
        with scenario_cols[1]:
            st.markdown("**Scenario B**")
            for column in slider_candidates:
                scenario_b[column] = st.slider(
                    f"B - {column}",
                    min_value=float(reference[column]) * 0.5,
                    max_value=float(reference[column]) * 1.5 + 1,
                    value=float(reference[column]),
                )

        if st.button("Compare scenarios", type="primary"):
            st.session_state.simulation = api_post(
                "/simulate",
                json={
                    "dataset_id": dataset_id,
                    "model_id": training["model_id"],
                    "changes": scenario_a,
                    "comparison_changes": scenario_b,
                },
            )
            st.session_state.actions = None

        simulation = st.session_state.get("simulation")
        if simulation:
            sim_metrics = st.columns(4)
            sim_metrics[0].metric("Baseline", simulation["prediction_before"])
            sim_metrics[1].metric("Scenario A", simulation["prediction_after"])
            sim_metrics[2].metric("Delta", simulation["delta"])
            sim_metrics[3].metric("Delta %", simulation["delta_pct"] if simulation["delta_pct"] is not None else "N/A")
            render_card("Scenario A Summary", simulation["impact_summary"])
            if simulation.get("comparison_prediction_after") is not None:
                render_card(
                    "Scenario B Summary",
                    simulation["comparison_summary"] or f"Scenario B prediction: {simulation['comparison_prediction_after']}",
                )
            render_card(
                "Confidence & Guardrails",
                (
                    f"Confidence level: <strong>{simulation['confidence_level']}</strong><br>"
                    f"Data coverage: <strong>{simulation['data_coverage_pct']}%</strong><br>"
                    f"{simulation['guardrail_note']}"
                ),
            )

with tabs[5]:
    st.subheader("Recommended Actions")
    actions = ensure_actions(dataset_id)
    for item in actions["recommended_actions"]:
        render_card(
            f"{item['title']} [{item['priority']}]",
            f"{item['rationale']}<br><br><strong>Expected effect:</strong> {item['expected_effect']}",
        )

with tabs[6]:
    st.subheader("Executive Summary")
    if st.button("Generate structured business report", type="primary"):
        payload = {
            "dataset_id": dataset_id,
            "profile": st.session_state.profile,
            "investigation": st.session_state.investigation,
            "training": st.session_state.get("training"),
            "simulation": st.session_state.get("simulation"),
        }
        st.session_state.summary = api_post("/summary", json=payload)

    summary = st.session_state.get("summary")
    if summary:
        render_card(summary["headline"], summary["executive_summary"])
        cols = st.columns(2, vertical_alignment="top")
        with cols[0]:
            render_card("Key Findings", "<br>".join(f"- {item}" for item in summary["key_findings"]))
            render_card("Main Drivers", "<br>".join(f"- {item}" for item in summary["main_drivers"]))
            render_card("Opportunities", "<br>".join(f"- {item}" for item in summary["opportunities"]))
        with cols[1]:
            render_card("Risks", "<br>".join(f"- {item}" for item in summary["risks"]))
            render_card("Recommended Actions", "<br>".join(f"- {item}" for item in summary["recommendations"]))
            render_card("Limitations", "<br>".join(f"- {item}" for item in summary["limitations"]))
    else:
        st.info("Generate the report to produce the structured consulting-style summary.")

st.caption("This is based on model behavior, not causal inference.")
