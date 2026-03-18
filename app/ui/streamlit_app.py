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
    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(211,131,54,0.14), transparent 26%),
            radial-gradient(circle at top right, rgba(47,109,73,0.18), transparent 30%),
            linear-gradient(180deg, #faf6f0 0%, #f1e8da 100%);
        color: #1f261f;
        font-family: 'Space Grotesk', sans-serif;
    }
    [data-testid="stHeader"] { background: transparent; }
    .hero, .card, .metric, .insight {
        background: rgba(255,252,247,0.84);
        border: 1px solid rgba(22,56,40,0.12);
        border-radius: 24px;
        box-shadow: 0 20px 50px rgba(30,29,23,0.08);
    }
    .hero { padding: 2rem 2.2rem; margin-bottom: 1rem; }
    .hero-kicker, .meta {
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: .12em;
        text-transform: uppercase;
        font-size: .78rem;
        color: #2f6d49;
    }
    .hero-title { color: #163828; font-size: 3rem; line-height: .96; margin: .45rem 0 .7rem 0; }
    .card { padding: 1.05rem 1.15rem; margin-bottom: 1rem; }
    .metric { padding: 1rem 1.1rem; min-height: 116px; }
    .metric-value { color: #163828; font-size: 1.9rem; font-weight: 700; }
    .insight { padding: 1rem 1.1rem; margin-bottom: .8rem; border-left: 8px solid #2f6d49; }
    .insight.high { border-left-color: #b44747; }
    .insight.medium { border-left-color: #d38336; }
    .insight.low { border-left-color: #2f6d49; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,252,247,0.84);
        border-radius: 999px;
        border: 1px solid rgba(22,56,40,0.12);
        padding: .55rem .95rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

API_BASE_URL = get_settings().api_base_url.rstrip("/")


def api_get(path: str) -> list | dict:
    response = requests.get(f"{API_BASE_URL}{path}", timeout=90)
    response.raise_for_status()
    return response.json()


def api_post(path: str, json: dict | None = None, files: dict | None = None) -> dict:
    response = requests.post(f"{API_BASE_URL}{path}", json=json, files=files, timeout=90)
    response.raise_for_status()
    return response.json()


def register_dataset(dataset: dict) -> None:
    catalog = st.session_state.setdefault("datasets_catalog", [])
    if not any(item["dataset_id"] == dataset["dataset_id"] for item in catalog):
        catalog.append(dataset)


def reset_analysis_state() -> None:
    for key in [
        "profile",
        "investigation",
        "training",
        "simulation",
        "summary",
        "actions",
        "focused_analysis",
        "root_cause",
        "enrichment",
        "copilot_answer",
        "merge_preview",
        "uploaded_file_name",
    ]:
        st.session_state.pop(key, None)


def bootstrap_sample() -> None:
    if "dataset" not in st.session_state:
        dataset = api_post("/upload/sample")
        st.session_state.dataset = dataset
        register_dataset(dataset)


def render_card(title: str, body: str) -> None:
    st.markdown(f'<div class="card"><strong>{title}</strong><div style="margin-top:.45rem;">{body}</div></div>', unsafe_allow_html=True)


def render_metric(label: str, value: str, foot: str) -> None:
    st.markdown(
        f'<div class="metric"><div class="meta">{label}</div><div class="metric-value">{value}</div><div>{foot}</div></div>',
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

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">AI Decision Copilot</div>
        <div class="hero-title">Investigate, predict, simulate, and recommend like a business analyst.</div>
        <div>
            This product combines dataset profiling, investigation suggestions, explainable modeling,
            scenario comparison, root-cause analysis, enrichment ideas, and an AI business copilot.
        </div>
        <div class="meta" style="margin-top:1rem;">upload -> diagnose -> investigate -> explain -> simulate -> recommend -> report</div>
    </div>
    """,
    unsafe_allow_html=True,
)

u_left, u_right = st.columns([1.05, 0.95], vertical_alignment="center")
with u_left:
    uploaded_file = st.file_uploader("Upload a CSV", type=["csv"])
with u_right:
    st.write("Use the built-in sample dataset or upload more files to unlock merge preview.")
    if st.button("Reload sample dataset", use_container_width=True):
        reset_analysis_state()
        dataset = api_post("/upload/sample")
        st.session_state.dataset = dataset
        register_dataset(dataset)

if uploaded_file is not None and st.session_state.get("uploaded_file_name") != uploaded_file.name:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
    reset_analysis_state()
    dataset = api_post("/upload", files=files)
    st.session_state.dataset = dataset
    st.session_state.uploaded_file_name = uploaded_file.name
    register_dataset(dataset)

dataset = st.session_state.dataset
dataset_id = dataset["dataset_id"]
profile = st.session_state.get("profile") or api_post("/profile", json={"dataset_id": dataset_id})
investigation = st.session_state.get("investigation") or api_post("/investigate", json={"dataset_id": dataset_id})
st.session_state.profile = profile
st.session_state.investigation = investigation

metric_cols = st.columns(5)
with metric_cols[0]:
    render_metric("Rows", str(profile["shape"]["rows"]), "Records available")
with metric_cols[1]:
    render_metric("Coverage", f"{profile['data_coverage_pct']}%", "Observed data completeness")
with metric_cols[2]:
    render_metric("Insights", str(len(investigation["insights"])), "Ranked by importance")
with metric_cols[3]:
    render_metric("Suggestions", str(len(investigation["investigation_suggestions"])), "Agent-led investigation paths")
with metric_cols[4]:
    render_metric("Datasets", str(len(st.session_state.get("datasets_catalog", []))), "Loaded in this session")

intro_cols = st.columns([1.2, 0.8], vertical_alignment="top")
with intro_cols[0]:
    render_card("Executive Brief", investigation["executive_brief"])
with intro_cols[1]:
    render_card("Guardrail", "This analysis is based on statistical patterns, not causal inference.")

tabs = st.tabs(
    [
        "Diagnostic",
        "Investigation",
        "Prediction",
        "Scenario Simulation",
        "Root Cause",
        "Enrichment",
        "Multi-Dataset",
        "Decision Copilot",
        "Executive Summary",
    ]
)

with tabs[0]:
    cols = st.columns([0.95, 1.05], vertical_alignment="top")
    with cols[0]:
        render_card("Headline Findings", "<br>".join(profile["headline_findings"]))
        render_card("Suggested Targets", ", ".join(profile["target_candidates"]) or "No obvious target")
        render_card("Derived Features", "<br>".join(f"- {item}" for item in profile["derived_features"]) or "No derived features")
        render_card(
            "Preview",
            f"Current dataset: <strong>{dataset['filename']}</strong><br>Rows: {dataset['rows']}<br>Columns: {dataset['columns']}",
        )
    with cols[1]:
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
        cols = st.columns([0.76, 0.24], vertical_alignment="center")
        with cols[0]:
            render_card(
                suggestion["title"],
                f"{suggestion['explanation']}<br><br><strong>Expected business impact:</strong> focus analyst attention on a potentially material performance driver.",
            )
        with cols[1]:
            if st.button("Investigate", key=f"invest_{suggestion['suggestion_id']}", use_container_width=True):
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
        render_card(focused["title"], f"{focused['analysis']}<br><br><strong>Business implication:</strong> {focused['business_implication']}")
        st.json(focused["supporting_stats"])
        if focused.get("chart_spec"):
            st.plotly_chart(go.Figure(focused["chart_spec"]), use_container_width=True)

    st.markdown("### Ranked Insights")
    for insight in investigation["insights"]:
        st.markdown(
            f"""
            <div class="insight {insight['impact_level']}">
                <strong>{insight['title']}</strong>
                <div style="margin-top:.35rem;">{insight['description']}</div>
                <div class="meta" style="margin-top:.45rem;">{insight['icon']} | type={insight['insight_type']} | impact={insight['impact_level']} | confidence={insight['confidence_pct']}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    render_card("Opportunity Areas", "<br>".join(f"- {item}" for item in investigation["opportunity_areas"]))
    render_card("Anomaly Narrative", investigation["anomaly_narrative"])
    for chart_spec in investigation["chart_specs"]:
        st.plotly_chart(go.Figure(chart_spec), use_container_width=True)

with tabs[2]:
    target_candidates = profile["target_candidates"] or profile["columns"]
    selected_target = st.selectbox("Choose a target to model", target_candidates)
    if st.button("Train prediction engine", type="primary"):
        st.session_state.training = api_post("/train", json={"dataset_id": dataset_id, "target": selected_target})
        st.session_state.actions = None
    training = st.session_state.get("training")
    if training:
        cols = st.columns([0.85, 1.15], vertical_alignment="top")
        with cols[0]:
            render_card(
                "Model trained successfully",
                (
                    f"Model type: <strong>{training['task_type']}</strong><br>"
                    f"Model: <strong>{training['model_name']}</strong><br>"
                    f"{training['primary_metric_name'].upper()} = <strong>{training['primary_metric_value']}</strong><br>"
                    f"Confidence: <strong>{training['confidence_level']}</strong><br>"
                    f"Data coverage: <strong>{training['data_coverage_pct']}%</strong>"
                ),
            )
            render_card("Top features", "<br>".join(f"{idx + 1}. {driver}" for idx, driver in enumerate(training["top_drivers"][:5])))
            st.caption("Metrics")
            st.json(training["metrics"])
            st.caption("Baseline comparison")
            st.json(training["baseline_metrics"])
        with cols[1]:
            st.plotly_chart(go.Figure(training["feature_importance_chart"]), use_container_width=True)
            st.dataframe(pd.DataFrame(training["feature_importance"][:5]), use_container_width=True, hide_index=True)
    else:
        st.info("Train a model to unlock richer simulation and copilot answers.")

with tabs[3]:
    training = st.session_state.get("training")
    if not training:
        st.info("Train a model first.")
    else:
        reference = training["reference_row"]
        slider_candidates = [col for col in ["price", "marketing_spend", "discount_pct"] if col in reference]
        a_col, b_col = st.columns(2, vertical_alignment="top")
        scenario_a: dict[str, object] = {}
        scenario_b: dict[str, object] = {}
        with a_col:
            st.markdown("**Scenario A**")
            for col in slider_candidates:
                scenario_a[col] = st.slider(
                    f"A - {col}",
                    min_value=float(reference[col]) * 0.5,
                    max_value=float(reference[col]) * 1.5 + 1,
                    value=float(reference[col]),
                )
        with b_col:
            st.markdown("**Scenario B**")
            for col in slider_candidates:
                scenario_b[col] = st.slider(
                    f"B - {col}",
                    min_value=float(reference[col]) * 0.5,
                    max_value=float(reference[col]) * 1.5 + 1,
                    value=float(reference[col]),
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
            metrics = st.columns(4)
            metrics[0].metric("Baseline", simulation["prediction_before"])
            metrics[1].metric("Scenario A", simulation["prediction_after"])
            metrics[2].metric("Delta", simulation["delta"])
            metrics[3].metric("Delta %", simulation["delta_pct"] if simulation["delta_pct"] is not None else "N/A")
            render_card("Scenario A Summary", simulation["impact_summary"])
            if simulation.get("comparison_prediction_after") is not None:
                render_card("Scenario B Summary", simulation["comparison_summary"] or f"Scenario B prediction: {simulation['comparison_prediction_after']}")
            render_card(
                "Confidence & Guardrails",
                (
                    f"Confidence level: <strong>{simulation['confidence_level']}</strong><br>"
                    f"Data coverage: <strong>{simulation['data_coverage_pct']}%</strong><br>"
                    f"{simulation['guardrail_note']}"
                ),
            )

with tabs[4]:
    root_metric = st.selectbox("Metric to explain", [col for col in profile["columns"] if col in profile["numeric_columns"]] or profile["columns"])
    if st.button("Explain root cause", type="primary"):
        st.session_state.root_cause = api_post("/root-cause", json={"dataset_id": dataset_id, "metric": root_metric})
    root_cause = st.session_state.get("root_cause")
    if root_cause:
        render_card("Why did this happen?", root_cause["explanation"])
        for driver in root_cause["main_drivers"]:
            render_card(driver["driver"], f"{driver['explanation']}<br><strong>Impact:</strong> {driver['impact_estimate']}")
        render_card("Evidence", "<br>".join(f"- {item}" for item in root_cause["evidence"]))
        if root_cause.get("chart_spec"):
            st.plotly_chart(go.Figure(root_cause["chart_spec"]), use_container_width=True)

with tabs[5]:
    if st.button("Suggest missing useful data", type="primary"):
        st.session_state.enrichment = api_post("/enrichment-suggestions", json={"dataset_id": dataset_id})
    enrichment = st.session_state.get("enrichment")
    if enrichment:
        for item in enrichment["suggestions"]:
            render_card(
                item["dataset_name"],
                (
                    f"<strong>Why it matters:</strong> {item['why_it_matters']}<br><br>"
                    f"<strong>How to integrate:</strong> {item['integration_hint']}<br><br>"
                    f"<strong>Expected value:</strong> {item['expected_value']}"
                ),
            )
    else:
        st.info("Ask the agent to suggest useful missing datasets such as campaigns, calendar effects, or segment data.")

with tabs[6]:
    datasets_catalog = st.session_state.get("datasets_catalog", [])
    if len(datasets_catalog) < 2:
        st.info("Upload at least two datasets in this session to preview a merge.")
    else:
        labels = {item["filename"]: item["dataset_id"] for item in datasets_catalog}
        left_name = st.selectbox("Left dataset", list(labels.keys()), key="merge_left")
        right_options = [name for name in labels.keys() if name != left_name]
        right_name = st.selectbox("Right dataset", right_options, key="merge_right")
        if st.button("Preview merge", type="primary"):
            st.session_state.merge_preview = api_post(
                "/merge-preview",
                json={"left_dataset_id": labels[left_name], "right_dataset_id": labels[right_name]},
            )
        preview = st.session_state.get("merge_preview")
        if preview:
            render_card("Merge Recommendation", preview["explanation"])
            render_card(
                "Join suggestion",
                (
                    f"Suggested keys: <strong>{', '.join(preview['suggested_join_keys']) or 'none'}</strong><br>"
                    f"Readiness: <strong>{preview['merge_readiness']}</strong><br>"
                    f"Estimated overlap rows: <strong>{preview['estimated_overlap_rows']}</strong>"
                ),
            )
            if preview["preview"]:
                st.dataframe(pd.DataFrame(preview["preview"]), use_container_width=True, hide_index=True)

with tabs[7]:
    question = st.text_area(
        "Ask a business question",
        placeholder="Should we increase price? Why did revenue drop? Where should we invest?",
    )
    copilot_target = st.text_input("Optional target override", value="revenue")
    if st.button("Ask the decision copilot", type="primary") and question.strip():
        st.session_state.copilot_answer = api_post(
            "/copilot/ask",
            json={"dataset_id": dataset_id, "question": question, "target": copilot_target or None},
        )
    answer = st.session_state.get("copilot_answer")
    if answer:
        render_card("Answer", answer["answer"])
        render_card("Intent", answer["intent"])
        render_card("Key Drivers", "<br>".join(f"- {item}" for item in answer["key_drivers"]))
        render_card("Evidence", "<br>".join(f"- {item}" for item in answer["evidence"]))
        if answer.get("simulation_result"):
            render_card("Simulation Result", answer["simulation_result"])
        render_card("Confidence", answer["confidence_level"])
        render_card("Recommended Actions", "<br>".join(f"- {item}" for item in answer["recommended_actions"]))

with tabs[8]:
    actions = ensure_actions(dataset_id)
    if st.button("Generate consulting-style report", type="primary"):
        st.session_state.summary = api_post(
            "/summary",
            json={
                "dataset_id": dataset_id,
                "profile": st.session_state.profile,
                "investigation": st.session_state.investigation,
                "training": st.session_state.get("training"),
                "simulation": st.session_state.get("simulation"),
            },
        )
    summary = st.session_state.get("summary")
    if summary:
        render_card(summary["headline"], summary["executive_summary"])
        cols = st.columns(2, vertical_alignment="top")
        with cols[0]:
            render_card("Key Insights", "<br>".join(f"- {item}" for item in summary["key_findings"]))
            render_card("Drivers", "<br>".join(f"- {item}" for item in summary["main_drivers"]))
            render_card("Opportunities", "<br>".join(f"- {item}" for item in summary["opportunities"]))
        with cols[1]:
            render_card("Risks", "<br>".join(f"- {item}" for item in summary["risks"]))
            render_card("Recommendations", "<br>".join(f"- {item}" for item in summary["recommendations"]))
            render_card("Limitations", "<br>".join(f"- {item}" for item in summary["limitations"]))
    st.markdown("### Recommended Actions")
    for item in actions["recommended_actions"]:
        render_card(f"{item['title']} [{item['priority']}]", f"{item['rationale']}<br><br><strong>Expected effect:</strong> {item['expected_effect']}")

st.caption("This analysis is based on statistical patterns, not causal inference.")
