from __future__ import annotations

import atexit
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlparse
from uuid import uuid4

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import get_settings
from app.services.charts import build_data_quality_chart
from app.ui.i18n import t


st.set_page_config(page_title="AI Decision Copilot", page_icon="AI", layout="wide")

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
        background: rgba(255,252,247,0.86);
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
    .section-head {
        margin: 1.8rem 0 .85rem 0;
    }
    .section-title {
        color: #163828;
        font-size: 1.38rem;
        font-weight: 700;
        margin-bottom: .2rem;
    }
    .section-subtitle {
        color: #48534a;
        max-width: 820px;
        font-size: .98rem;
    }
    .decision-shell {
        background: linear-gradient(180deg, rgba(255,252,247,0.96), rgba(249,242,231,0.92));
        border: 1px solid rgba(22,56,40,0.16);
        border-radius: 28px;
        padding: 1.25rem;
        box-shadow: 0 26px 60px rgba(24,31,25,0.12);
        margin-bottom: 1.25rem;
    }
    .decision-card {
        background: rgba(255,255,255,0.68);
        border: 1px solid rgba(22,56,40,0.10);
        border-radius: 22px;
        padding: 1rem 1rem 1.05rem 1rem;
        min-height: 168px;
    }
    .decision-card.accent {
        background: linear-gradient(180deg, rgba(244,248,242,0.98), rgba(233,242,234,0.92));
        border-color: rgba(47,109,73,0.22);
    }
    .decision-icon {
        font-size: 1.2rem;
        margin-bottom: .45rem;
    }
    .decision-label {
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: .1em;
        text-transform: uppercase;
        font-size: .72rem;
        color: #5b685d;
        margin-bottom: .45rem;
    }
    .decision-message {
        color: #163828;
        font-size: 1.1rem;
        line-height: 1.3;
        font-weight: 700;
    }
    .decision-foot {
        margin-top: .65rem;
        color: #4d584f;
        font-size: .9rem;
    }
    .insight-premium {
        background: rgba(255,252,247,0.92);
        border: 1px solid rgba(22,56,40,0.10);
        border-radius: 24px;
        padding: 1.05rem 1.1rem 1.1rem 1.1rem;
        box-shadow: 0 16px 34px rgba(30,29,23,0.06);
        min-height: 178px;
    }
    .insight-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: .6rem;
        margin-bottom: .7rem;
    }
    .insight-icon {
        font-size: 1.15rem;
    }
    .tag {
        display: inline-block;
        border-radius: 999px;
        padding: .24rem .55rem;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .04em;
        background: rgba(22,56,40,0.08);
        color: #163828;
    }
    .tag.high {
        background: rgba(180,71,71,0.12);
        color: #8c2f2f;
    }
    .tag.medium {
        background: rgba(211,131,54,0.16);
        color: #9a5a18;
    }
    .tag.low {
        background: rgba(47,109,73,0.14);
        color: #245239;
    }
    .story-box {
        background: rgba(255,252,247,0.92);
        border: 1px solid rgba(22,56,40,0.11);
        border-radius: 22px;
        padding: .95rem 1rem;
        margin-bottom: .7rem;
    }
    .story-box strong {
        color: #163828;
    }
    .suggestion-card {
        background: rgba(255,252,247,0.9);
        border: 1px solid rgba(22,56,40,0.10);
        border-radius: 22px;
        padding: 1rem 1rem 1.1rem 1rem;
        min-height: 190px;
        box-shadow: 0 16px 36px rgba(30,29,23,0.06);
    }
    .support-note {
        color: #58655b;
        font-size: .92rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,252,247,0.84);
        border-radius: 999px;
        border: 1px solid rgba(22,56,40,0.12);
        padding: .55rem .95rem;
    }
    div.stButton > button {
        border-radius: 16px;
        border: 1px solid rgba(22,56,40,0.14);
        background: rgba(255,252,247,0.95);
        color: #163828;
        padding: .55rem .95rem;
        font-weight: 600;
        box-shadow: 0 10px 22px rgba(24,31,25,0.05);
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(180deg, #2f6d49 0%, #245239 100%);
        color: #fffdf8;
        border-color: rgba(47,109,73,0.4);
    }
</style>
""",
    unsafe_allow_html=True,
)

SETTINGS = get_settings()
API_BASE_URL = SETTINGS.api_base_url.rstrip("/")


def _is_local_api_url(api_base_url: str) -> bool:
    parsed = urlparse(api_base_url)
    return parsed.hostname in {"127.0.0.1", "localhost"}


def _api_healthcheck(api_base_url: str, timeout: float = 1.0) -> dict | None:
    try:
        response = requests.get(f"{api_base_url}/health", timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def ensure_local_api_server(api_base_url: str, auto_start: bool) -> subprocess.Popen[str] | None:
    if not auto_start or not _is_local_api_url(api_base_url) or _api_healthcheck(api_base_url):
        return None

    parsed = urlparse(api_base_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8000
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT_DIR}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.api.main:app",
            "--host",
            host,
            "--port",
            str(port),
        ],
        cwd=str(ROOT_DIR),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    atexit.register(lambda: process.poll() is None and process.terminate())
    for _ in range(30):
        if _api_healthcheck(api_base_url):
            return process
        time.sleep(0.5)
    return process


def api_get(path: str) -> list | dict:
    response = requests.get(f"{API_BASE_URL}{path}", timeout=90)
    response.raise_for_status()
    return response.json()


def api_post(path: str, json: dict | None = None, files: dict | None = None) -> dict:
    response = requests.post(f"{API_BASE_URL}{path}", json=json, files=files, timeout=90)
    response.raise_for_status()
    return response.json()


def ensure_session() -> str:
    if "copilot_session_id" not in st.session_state:
        st.session_state.copilot_session_id = str(uuid4())
    if "lang" not in st.session_state:
        st.session_state.lang = "fr"
    return st.session_state.copilot_session_id


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
        "decision_engine",
        "decision_engine_meta",
        "decision_engine_meta_signature",
        "summary",
        "actions",
        "focused_analysis",
        "root_cause",
        "enrichment",
        "copilot_answer",
        "merge_preview",
        "report_export",
        "uploaded_file_name",
    ]:
        st.session_state.pop(key, None)


def bootstrap_sample() -> None:
    if "dataset" not in st.session_state:
        dataset = api_post("/upload/sample")
        st.session_state.dataset = dataset
        register_dataset(dataset)


def load_named_sample(sample_name: str) -> None:
    reset_analysis_state()
    dataset = api_post(f"/upload/sample/{sample_name}")
    st.session_state.dataset = dataset
    register_dataset(dataset)


def render_card(title: str, body: str) -> None:
    st.markdown(f'<div class="card"><strong>{title}</strong><div style="margin-top:.45rem;">{body}</div></div>', unsafe_allow_html=True)


def render_metric(label: str, value: str, foot: str) -> None:
    st.markdown(
        f'<div class="metric"><div class="meta">{label}</div><div class="metric-value">{value}</div><div>{foot}</div></div>',
        unsafe_allow_html=True,
    )


def render_primary_card(title: str, body: str, footnote: str | None = None) -> None:
    footer_html = f'<div class="meta" style="margin-top:.8rem;">{footnote}</div>' if footnote else ""
    st.markdown(
        (
            '<div class="card" style="padding:1.4rem 1.5rem; border:1px solid rgba(22,56,40,0.18); '
            'box-shadow:0 24px 55px rgba(24,31,25,0.12);">'
            '<div class="meta">{title}</div>'
            '<div style="font-size:1.5rem; font-weight:700; color:#163828; margin-top:.55rem; line-height:1.25;">{body}</div>'
            f"{footer_html}"
            "</div>"
        ).format(title=title, body=body),
        unsafe_allow_html=True,
    )


def render_insight_panel(title: str, summary: str, why_it_matters: str, impact_level: str, confidence: str, lang: str) -> None:
    impact_color = {"high": "#b44747", "medium": "#d38336", "low": "#2f6d49"}.get(impact_level, "#607087")
    st.markdown(
        (
            '<div class="card" style="border-left:8px solid {impact_color};">'
            '<div class="meta">{key_message}</div>'
            "<strong>{title}</strong>"
            '<div style="margin-top:.45rem;">{summary}</div>'
            '<div style="margin-top:.7rem;"><strong>{why_label}:</strong> {why}</div>'
            '<div class="meta" style="margin-top:.8rem;">{impact_label}={impact} | {confidence_label}={confidence}</div>'
            "</div>"
        ).format(
            impact_color=impact_color,
            key_message=t("insight.key_message", lang),
            title=title,
            summary=summary,
            why_label=t("insight.why_it_matters", lang),
            why=why_it_matters,
            impact_label=t("insight.impact", lang),
            impact=impact_level,
            confidence_label=t("insight.confidence", lang),
            confidence=confidence,
        ),
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="section-head"><div class="section-title">{title}</div><div class="section-subtitle">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )


def render_decision_card(icon: str, label: str, message: str, footnote: str | None = None, accent: bool = False) -> None:
    foot_html = f'<div class="decision-foot">{footnote}</div>' if footnote else ""
    accent_class = " accent" if accent else ""
    st.markdown(
        (
            f'<div class="decision-card{accent_class}">'
            f'<div class="decision-icon">{icon}</div>'
            f'<div class="decision-label">{label}</div>'
            f'<div class="decision-message">{message}</div>'
            f"{foot_html}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_premium_insight_card(icon: str, title: str, summary: str, impact_level: str) -> None:
    impact_key = impact_level.lower()
    tag_label = {
        "high": "High impact",
        "medium": "Medium impact",
        "low": "Low impact",
    }.get(impact_key, impact_level.title())
    st.markdown(
        (
            '<div class="insight-premium">'
            '<div class="insight-row">'
            f'<div class="insight-icon">{icon}</div>'
            f'<span class="tag {impact_key}">{tag_label}</span>'
            "</div>"
            f"<strong>{title}</strong>"
            f'<div style="margin-top:.55rem;">{summary}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_chart_story_box(chart_spec: dict, lang: str) -> None:
    impact = confidence_label(chart_spec.get("impact_level", "medium"), lang)
    st.markdown(
        (
            '<div class="story-box">'
            f"<strong>{'What this shows' if lang == 'en' else 'Ce que cela montre'}:</strong> {chart_spec['insight']}<br>"
            f"<strong>{'Why it matters' if lang == 'en' else 'Pourquoi c est important'}:</strong> {chart_spec['why_it_matters']}<br>"
            f"<strong>{'Impact' if lang == 'en' else 'Impact'}:</strong> {impact}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_annotated_chart(chart_spec: dict, key: str, annotation_text: str) -> None:
    figure = go.Figure(chart_spec["figure"])
    figure.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=annotation_text,
        showarrow=False,
        align="left",
        bgcolor="rgba(255,252,247,0.96)",
        bordercolor="rgba(22,56,40,0.18)",
        borderwidth=1,
        borderpad=6,
        font={"size": 12, "color": "#163828"},
    )
    st.plotly_chart(figure, use_container_width=True, key=key)


def to_float_if_possible(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def labelize_decision(value: str) -> str:
    return value.replace("_", " ").title()


def humanize_decision_choice(value: str, lang: str) -> str:
    return {
        "baseline": "Keep baseline" if lang == "en" else "Conserver la reference",
        "scenario_a": "Scenario A" if lang == "en" else "Scenario A",
        "scenario_b": "Scenario B" if lang == "en" else "Scenario B",
    }.get(value, value)


def humanize_intent(value: str, lang: str) -> str:
    mapping = {
        "diagnosis": "Diagnosis" if lang == "en" else "Diagnostic",
        "root_cause": "Root cause" if lang == "en" else "Cause racine",
        "prediction": "Prediction" if lang == "en" else "Prediction",
        "simulation": "Simulation" if lang == "en" else "Simulation",
        "prioritization": "Prioritization" if lang == "en" else "Priorisation",
        "segment_analysis": "Segment analysis" if lang == "en" else "Analyse de segment",
        "anomaly_investigation": "Anomaly investigation" if lang == "en" else "Investigation d'anomalie",
        "data_gap": "Missing data" if lang == "en" else "Donnees manquantes",
        "enrichment": "Enrichment" if lang == "en" else "Enrichissement",
        "merge": "Merge suggestion" if lang == "en" else "Suggestion de fusion",
    }
    return mapping.get(value, value.replace("_", " ").title())


def html_bullets(items: list[str]) -> str:
    return "<br>".join(f"- {item}" for item in items)


def confidence_label(level: str, lang: str) -> str:
    if lang == "fr":
        return {"high": "elevee", "medium": "moyenne", "low": "faible"}.get(level, level)
    return level


def priority_label(level: str, lang: str) -> str:
    return confidence_label(level, lang)


def detect_business_levers(profile: dict, lang: str) -> list[str]:
    columns = [column.lower() for column in profile["columns"]]
    levers: list[str] = []
    if any(keyword in column for column in columns for keyword in ["price", "discount"]):
        levers.append("Pricing and discount strategy" if lang == "en" else "Strategie prix et remise")
    if any(keyword in column for column in columns for keyword in ["marketing", "campaign", "spend"]):
        levers.append("Marketing allocation" if lang == "en" else "Allocation marketing")
    if any(keyword in column for column in columns for keyword in ["region", "segment", "channel", "customer"]):
        levers.append("Segment and regional prioritization" if lang == "en" else "Priorisation segment et region")
    if any(keyword in column for column in columns for keyword in ["product", "sku", "category", "mix"]):
        levers.append("Product mix and assortment" if lang == "en" else "Mix produit et assortiment")
    if profile.get("temporal_columns"):
        levers.append("Trend and anomaly monitoring" if lang == "en" else "Suivi de tendance et d'anomalies")
    if not levers:
        levers.append("Baseline operational diagnosis" if lang == "en" else "Diagnostic operationnel de base")
    return levers[:5]


def suggest_demo_paths(profile: dict, lang: str) -> list[str]:
    columns = [column.lower() for column in profile["columns"]]
    suggestions: list[str] = []
    if "revenue" in columns or "sales" in columns:
        suggestions.append("Explain revenue changes" if lang == "en" else "Expliquer les variations de revenu")
    if any(keyword in column for column in columns for keyword in ["price", "discount"]):
        suggestions.append("Test pricing scenarios safely" if lang == "en" else "Tester des scenarios de prix de facon sure")
    if any(keyword in column for column in columns for keyword in ["marketing", "campaign", "spend"]):
        suggestions.append("Compare marketing return by scenario" if lang == "en" else "Comparer le retour marketing par scenario")
    if any(keyword in column for column in columns for keyword in ["region", "segment", "channel"]):
        suggestions.append("Prioritize high-value segments" if lang == "en" else "Prioriser les segments a forte valeur")
    if profile.get("temporal_columns"):
        suggestions.append("Investigate trend breaks and anomalies" if lang == "en" else "Investiguer les ruptures de tendance et anomalies")
    if not suggestions:
        suggestions.append("Start with automated investigation suggestions" if lang == "en" else "Commencer par les suggestions d'investigation automatiques")
    return suggestions[:5]


def dataset_snapshot_lines(dataset: dict, profile: dict, lang: str) -> list[str]:
    main_dimensions = ", ".join(profile["categorical_columns"][:4]) or t("app.none", lang)
    return [
        f"{t('app.current_dataset', lang)}: <strong>{dataset['filename']}</strong>",
        f"{t('app.rows_and_columns', lang)}: <strong>{dataset['rows']} / {dataset['columns']}</strong>",
        f"{t('app.time_signal', lang)}: <strong>{t('app.yes', lang) if profile.get('temporal_columns') else t('app.no', lang)}</strong>",
        f"{t('app.main_dimensions', lang)}: <strong>{main_dimensions}</strong>",
        f"{t('app.quality_score', lang)}: <strong>{profile['quality_score']}</strong>",
    ]


def render_dataset_preview(dataset: dict) -> None:
    preview = dataset.get("preview") or []
    if preview:
        st.dataframe(pd.DataFrame(preview), use_container_width=True, hide_index=True)
    else:
        st.info(t("app.no_preview", st.session_state.lang))


def get_decision_summary_payload(lang: str, investigation: dict, decision: dict | None, answer: dict | None) -> dict[str, str]:
    if decision:
        next_analysis = decision.get("next_best_analysis") or t("app.not_available", lang)
        return {
            "recommendation": humanize_decision_choice(decision["recommended_decision"], lang),
            "risk": decision["main_risk"],
            "confidence": confidence_label(decision["confidence"]["level"], lang),
            "robustness": confidence_label(decision["robustness"], lang),
            "next_analysis": next_analysis,
        }

    if answer:
        next_items = answer.get("suggested_next_investigation") or []
        return {
            "recommendation": answer["answer"],
            "risk": answer.get("guardrail") or t("app.guardrail_body", lang),
            "confidence": confidence_label(answer["confidence_level"], lang),
            "robustness": answer.get("model_reliability") or ("directional" if lang == "en" else "directionnelle"),
            "next_analysis": next_items[0] if next_items else t("app.not_available", lang),
        }

    fallback_next = investigation["investigation_suggestions"][0]["title"] if investigation.get("investigation_suggestions") else t("app.not_available", lang)
    return {
        "recommendation": investigation["executive_brief"],
        "risk": t("app.guardrail_body", lang),
        "confidence": "medium" if lang == "en" else "moyenne",
        "robustness": "directional" if lang == "en" else "directionnelle",
        "next_analysis": fallback_next,
    }


def run_global_copilot_query(dataset_id: str, question: str, target: str | None = None) -> None:
    st.session_state.copilot_answer = api_post(
        "/copilot/ask",
        json={
            "dataset_id": dataset_id,
            "question": question,
            "target": target or None,
            "session_id": ensure_session(),
            "language": st.session_state.lang,
        },
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
                "language": st.session_state.lang,
            },
        )
    return st.session_state.actions


def load_dataset_context(dataset_id: str) -> tuple[dict, dict]:
    profile = st.session_state.get("profile") or api_post("/profile", json={"dataset_id": dataset_id, "language": st.session_state.lang})
    investigation = st.session_state.get("investigation") or api_post("/investigate", json={"dataset_id": dataset_id, "language": st.session_state.lang})
    st.session_state.profile = profile
    st.session_state.investigation = investigation
    return profile, investigation


def run_guided_demo(dataset_id: str) -> None:
    if "training" not in st.session_state:
        st.session_state.training = api_post("/train", json={"dataset_id": dataset_id, "target": "revenue"})
    training = st.session_state.training
    if "simulation" not in st.session_state:
        reference = training["reference_row"]
        changes = {}
        if "price" in reference:
            changes["price"] = float(reference["price"]) * 1.08
        if "marketing_spend" in reference:
            changes["marketing_spend"] = float(reference["marketing_spend"]) * 1.05
        if "discount_pct" in reference:
            changes["discount_pct"] = max(0.0, float(reference["discount_pct"]) - 1)
        st.session_state.simulation = api_post(
            "/simulate",
            json={"dataset_id": dataset_id, "model_id": training["model_id"], "changes": changes},
        )
    st.session_state.actions = None


ensure_session()
ensure_local_api_server(API_BASE_URL, getattr(SETTINGS, "auto_start_local_api", True))
api_health = _api_healthcheck(API_BASE_URL)
if not api_health:
    st.error(
        "The local API backend is unavailable. Start the API or keep AUTO_START_LOCAL_API=true."
        if st.session_state.lang == "en"
        else "Le backend API local est indisponible. Lancez l API ou laissez AUTO_START_LOCAL_API=true."
    )
    st.stop()
bootstrap_sample()
dataset = st.session_state.dataset
dataset_id = dataset["dataset_id"]
profile, investigation = load_dataset_context(dataset_id)

with st.sidebar:
    st.markdown(f"### {t('app.hero_kicker', st.session_state.lang)}")
    llm_label = (
        f"LLM: OpenAI ({api_health.get('llm_model', SETTINGS.openai_model)})"
        if api_health.get("llm_enabled") == "true"
        else "LLM: fallback mode"
    )
    st.caption(llm_label)
    previous_lang = st.session_state.lang
    st.session_state.lang = st.selectbox(
        t("decision_engine.language", st.session_state.lang),
        options=["fr", "en"],
        index=0 if st.session_state.lang == "fr" else 1,
        format_func=lambda value: value.upper(),
    )
    if st.session_state.lang != previous_lang:
        for key in ["profile", "investigation", "focused_analysis", "root_cause", "enrichment", "summary", "decision_engine", "decision_engine_meta", "decision_engine_meta_signature", "copilot_answer"]:
            st.session_state.pop(key, None)
        st.rerun()
    uploaded_file = st.file_uploader(t("app.upload_csv", st.session_state.lang), type=["csv"])
    st.caption(t("app.sample_hint", st.session_state.lang))
    if st.button(t("app.load_sales_demo", st.session_state.lang), use_container_width=True):
        load_named_sample("sales")
        run_guided_demo(st.session_state.dataset["dataset_id"])
        st.rerun()
    if st.button(t("app.load_marketing_demo", st.session_state.lang), use_container_width=True):
        load_named_sample("marketing")
        st.rerun()
    if st.button(t("app.reload_sample", st.session_state.lang), use_container_width=True):
        load_named_sample("sales")
        st.rerun()

if uploaded_file is not None and st.session_state.get("uploaded_file_name") != uploaded_file.name:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
    reset_analysis_state()
    dataset = api_post("/upload", files=files)
    st.session_state.dataset = dataset
    st.session_state.uploaded_file_name = uploaded_file.name
    register_dataset(dataset)
    st.rerun()

dataset = st.session_state.dataset
dataset_id = dataset["dataset_id"]
profile, investigation = load_dataset_context(dataset_id)
target_options = profile["target_candidates"] or profile["columns"] or ["revenue"]
lang = st.session_state.lang
hero_subtitle = (
    "Ask one business question, compare scenarios, and get a recommendation with guardrails."
    if lang == "en"
    else "Posez une question metier, comparez les scenarios et obtenez une recommandation avec garde-fous."
)

st.markdown(
    f"""
    <div class="hero" style="padding:1.7rem 1.9rem;">
        <div class="hero-kicker">{t("app.hero_kicker", lang)}</div>
        <div class="hero-title" style="font-size:2.6rem; max-width:980px;">{t("app.hero_title", lang)}</div>
        <div style="max-width:860px; font-size:1.04rem; color:#3d463e;">{hero_subtitle}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

default_global_target = "revenue" if "revenue" in target_options else target_options[0]
global_question_cols = st.columns([1.7, 0.75, 0.55], vertical_alignment="bottom")
with global_question_cols[0]:
    global_question = st.text_input(
        t("app.top_question", lang),
        placeholder=t("app.top_question_placeholder", lang),
        key="global_question_input",
    )
with global_question_cols[1]:
    global_target = st.selectbox(
        t("app.target_override", lang),
        target_options,
        index=target_options.index(default_global_target),
        key="global_target_override",
    )
with global_question_cols[2]:
    if st.button(t("app.top_question_button", lang), type="primary", use_container_width=True) and global_question.strip():
        run_global_copilot_query(dataset_id, global_question.strip(), global_target)

metric_cols = st.columns(3)
with metric_cols[0]:
    render_metric(t("app.metric.insights", lang), str(min(3, len(investigation["insights"]))), t("app.metric.insights_foot", lang))
with metric_cols[1]:
    render_metric(t("app.metric.coverage", lang), f"{profile['data_coverage_pct']}%", t("app.metric.coverage_foot", lang))
with metric_cols[2]:
    render_metric(t("app.metric.suggestions", lang), str(len(investigation["investigation_suggestions"][:3])), t("app.metric.suggestions_foot", lang))

decision = st.session_state.get("decision_engine")
copilot_answer = st.session_state.get("copilot_answer")
simulation = st.session_state.get("simulation")
summary_payload = get_decision_summary_payload(lang, investigation, decision, copilot_answer)

render_section_header(
    "Decision Summary" if lang == "en" else "Resume de decision",
    "What the copilot recommends now, why it matters, and how reliable it is."
    if lang == "en"
    else "Ce que le copilote recommande maintenant, pourquoi cela compte et a quel point la recommandation est fiable.",
)
st.markdown('<div class="decision-shell">', unsafe_allow_html=True)
decision_cards = st.columns(5)
decision_items = [
    (
        "🎯",
        "Recommendation" if lang == "en" else "Recommandation",
        summary_payload["recommendation"],
        t("decision_engine.core_card_caption", lang),
        True,
    ),
    (
        "⚠️",
        "Main risk" if lang == "en" else "Risque principal",
        summary_payload["risk"],
        None,
        False,
    ),
    (
        "📊",
        "Confidence" if lang == "en" else "Confiance",
        summary_payload["confidence"].title(),
        None,
        False,
    ),
    (
        "🧠",
        "Robustness" if lang == "en" else "Robustesse",
        summary_payload["robustness"].title(),
        None,
        False,
    ),
    (
        "➡️",
        "Next best action" if lang == "en" else "Prochaine action",
        summary_payload["next_analysis"],
        None,
        False,
    ),
]
for idx, item in enumerate(decision_items):
    with decision_cards[idx]:
        render_decision_card(item[0], item[1], item[2], item[3], accent=item[4])
st.markdown("</div>", unsafe_allow_html=True)

render_section_header(
    "What matters most now" if lang == "en" else "Ce qui compte le plus maintenant",
    "Three business signals to scan before making a decision."
    if lang == "en"
    else "Trois signaux business a lire avant de prendre une decision.",
)
top_insights = investigation["insights"][:3]
if top_insights:
    insight_cols = st.columns(min(3, len(top_insights)))
    insight_icons = {"high": "🔥", "medium": "📈", "low": "📉"}
    for idx, insight in enumerate(top_insights):
        with insight_cols[idx]:
            render_premium_insight_card(
                insight.get("icon") or insight_icons.get(insight["impact_level"], "⚠️"),
                insight["title"],
                insight["description"],
                insight["impact_level"],
            )

key_charts = investigation.get("chart_specs", [])[:2]
if key_charts:
    render_section_header(
        "Key charts" if lang == "en" else "Graphiques cles",
        "Each chart answers a business question and explains why the signal matters."
        if lang == "en"
        else "Chaque graphique repond a une question business et explique pourquoi le signal compte.",
    )
    chart_cols = st.columns(min(2, len(key_charts)))
    annotation_copy = [
        "Revenue drop starts here" if lang == "en" else "La baisse de revenu commence ici",
        "Scenario impact visible here" if lang == "en" else "Impact du scenario visible ici",
        "Anomaly detected" if lang == "en" else "Anomalie detectee",
    ]
    for idx, chart_spec in enumerate(key_charts):
        with chart_cols[idx]:
            render_chart_story_box(chart_spec, lang)
            st.caption(f"{chart_spec['question']} | {annotation_copy[idx % len(annotation_copy)]}")
            render_annotated_chart(chart_spec, f"overview_chart_{idx}", annotation_copy[idx % len(annotation_copy)])

if simulation:
    render_section_header(
        "Scenario impact" if lang == "en" else "Impact du scenario",
        "How the proposed change alters expected performance versus the current baseline."
        if lang == "en"
        else "Comment le changement propose modifie la performance attendue par rapport a la reference actuelle.",
    )
    sim_cols = st.columns(4)
    sim_cols[0].metric(t("decision_engine.before", lang), simulation["prediction_before"])
    sim_cols[1].metric(t("decision_engine.after", lang), simulation["prediction_after"])
    sim_cols[2].metric(t("decision_engine.delta", lang), simulation["delta"])
    sim_cols[3].metric(t("decision_engine.delta_pct", lang), simulation["delta_pct"] if simulation["delta_pct"] is not None else t("app.not_available", lang))
    narrative_cols = st.columns(2, vertical_alignment="top")
    with narrative_cols[0]:
        render_card("Scenario summary" if lang == "en" else "Resume du scenario", simulation["impact_summary"])
    with narrative_cols[1]:
        render_card(t("app.guardrail", lang), simulation["guardrail_note"])

render_section_header(
    t("investigation.suggestions", lang),
    "Actionable next analyses to validate the recommendation before acting."
    if lang == "en"
    else "Des analyses actionnables pour valider la recommandation avant de passer a l'action.",
)
suggestions = investigation["investigation_suggestions"][:4]
for row_start in range(0, len(suggestions), 2):
    row_items = suggestions[row_start:row_start + 2]
    suggestion_cols = st.columns(len(row_items))
    for idx, suggestion in enumerate(row_items):
        with suggestion_cols[idx]:
            st.markdown(
                (
                    '<div class="suggestion-card">'
                    f"<strong>{suggestion['title']}</strong>"
                    f'<div style="margin-top:.55rem;">{suggestion["explanation"]}</div>'
                    f'<div style="margin-top:.8rem;"><span class="tag high">{t("investigation.expected_impact", lang)}: {suggestion["expected_impact"]}</span></div>'
                    f'<div style="margin-top:.45rem;"><span class="tag medium">{t("investigation.confidence", lang)}: {suggestion.get("confidence_pct", 0)}%</span></div>'
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            if st.button(t("investigation.button", st.session_state.lang), key=f"invest_premium_{suggestion['suggestion_id']}", use_container_width=True):
                payload = dict(suggestion["payload"])
                payload["investigation_type"] = suggestion["investigation_type"]
                st.session_state.focused_analysis = api_post(
                    "/investigate-path",
                    json={"dataset_id": dataset_id, "suggestion_id": suggestion["suggestion_id"], "payload": payload, "language": st.session_state.lang},
                )

focused = st.session_state.get("focused_analysis")
if focused:
    render_card(
        focused["title"],
        f"{focused['analysis']}<br><br><strong>{t('investigation.business_implication', st.session_state.lang)}:</strong> {focused['business_implication']}",
    )
    if focused.get("chart_spec"):
        render_chart_story_box(
            {
                "insight": focused["business_implication"],
                "why_it_matters": focused["analysis"],
                "impact_level": "high",
            },
            lang,
        )
        render_annotated_chart(
            {"figure": focused["chart_spec"]},
            f"focused_chart_{focused['title']}",
            "Investigate this signal" if lang == "en" else "Explorer ce signal",
        )

with st.expander(t("decision_engine.evidence_pack", lang), expanded=False):
    st.markdown(
        f"<div class='support-note'>{'This recommendation is supported by the following evidence and model signals.' if lang == 'en' else 'Cette recommandation est soutenue par les preuves suivantes et par les signaux du modele.'}</div>",
        unsafe_allow_html=True,
    )
    if decision:
        evidence_cols = st.columns(2, vertical_alignment="top")
        with evidence_cols[0]:
            render_card(
                "Key metrics used" if lang == "en" else "Metriques utilisees",
                "<br>".join(f"<strong>{key}</strong>: {value}" for key, value in decision["evidence_pack"]["supporting_metrics"].items()),
            )
            render_card(
                "Top variables" if lang == "en" else "Variables majeures",
                html_bullets(decision["evidence_pack"]["top_variables"]),
            )
            render_card(
                "Supporting charts" if lang == "en" else "Graphiques d appui",
                html_bullets(decision["evidence_pack"]["chart_references"]),
            )
        with evidence_cols[1]:
            render_card(
                "Simulation details" if lang == "en" else "Details de simulation",
                html_bullets(decision["evidence_pack"]["scenario_assumptions"]),
            )
            render_card(
                "Data quality indicators" if lang == "en" else "Indicateurs de qualite",
                "<br>".join(f"- {item}" for item in decision["evidence_pack"]["quality_indicators"]),
            )
            render_card(
                t("decision_engine.supporting_evidence", lang),
                "<br>".join(f"- {item}" for item in decision["supporting_evidence"]),
            )
    else:
        training = st.session_state.get("training")
        evidence_cols = st.columns(2, vertical_alignment="top")
        with evidence_cols[0]:
            render_card(
                "Key metrics used" if lang == "en" else "Metriques utilisees",
                (
                    f"{t('app.quality_score', lang)}: <strong>{profile['quality_score']}</strong><br>"
                    f"{t('app.metric.coverage', lang)}: <strong>{profile['data_coverage_pct']}%</strong><br>"
                    f"{t('app.rows_and_columns', lang)}: <strong>{dataset['rows']} / {dataset['columns']}</strong>"
                ),
            )
            render_card(
                "Top variables" if lang == "en" else "Variables majeures",
                html_bullets(training["top_drivers"][:5] if training else profile["columns"][:5]),
            )
        with evidence_cols[1]:
            render_card(
                "Data quality indicators" if lang == "en" else "Indicateurs de qualite",
                "<br>".join(f"- {item}" for item in profile_quality_card["quality_indicators"]) if (profile_quality_card := build_data_quality_chart(profile, lang)).get("quality_indicators") else profile_quality_card["insight"],
            )
            render_card(
                "Supporting charts" if lang == "en" else "Graphiques d appui",
                html_bullets([chart["title"] for chart in investigation.get("chart_specs", [])[:3]]) or t("app.not_available", lang),
            )

with st.expander("Data details" if lang == "en" else "Details des donnees", expanded=False):
    snapshot_cols = st.columns([0.9, 1.1], vertical_alignment="top")
    with snapshot_cols[0]:
        render_card("Business Snapshot" if lang == "en" else "Business Snapshot", "<br>".join(dataset_snapshot_lines(dataset, profile, lang)))
        render_card("Signals used" if lang == "en" else "Signaux utilises", html_bullets(detect_business_levers(profile, lang)))
        render_card("Best next paths" if lang == "en" else "Meilleures prochaines pistes", html_bullets(suggest_demo_paths(profile, lang)))
    with snapshot_cols[1]:
        st.caption("Business Snapshot" if lang == "en" else "Business Snapshot")
        render_dataset_preview(dataset)
    st.markdown(f"#### {'Data reference' if lang == 'en' else 'Reference des donnees'}")
    st.dataframe(
        pd.DataFrame(
            {
                t("diagnostic.column", lang): profile["columns"],
                t("diagnostic.dtype", lang): [profile["dtypes"][col] for col in profile["columns"]],
                t("diagnostic.missing_pct", lang): [profile["missing_pct"][col] for col in profile["columns"]],
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(f"#### {'Signals created by the copilot' if lang == 'en' else 'Signaux crees par le copilote'}")
    render_card(
        t("diagnostic.derived_features", lang),
        "<br>".join(
            f"<strong>{item['feature']}</strong>: {item['reason']}"
            for item in profile.get("derived_feature_details", [])
        ) or t("diagnostic.no_derived_features", lang),
    )
    st.markdown(f"#### {'Data reliability' if lang == 'en' else 'Fiabilite des donnees'}")
    profile_quality_card = build_data_quality_chart(profile, lang)
    render_chart_story_box(profile_quality_card, lang)
    st.plotly_chart(go.Figure(profile_quality_card["figure"]), use_container_width=True, key="data_quality_chart_top")

with st.expander("Advanced analysis studio" if lang == "en" else "Studio d analyse avancee", expanded=False):
    tabs = st.tabs(
        [
            "Overview" if lang == "en" else "Vue d'ensemble",
            "Investigation" if lang == "en" else "Investigation",
            "Prediction" if lang == "en" else "Prediction",
            "Simulation" if lang == "en" else "Simulation",
            t("decision_engine.title", lang),
            t("decision_engine.evidence_pack", lang),
            "Data & Details" if lang == "en" else "Donnees & details",
        ]
    )

with tabs[0]:
    overview_cols = st.columns([1.15, 0.85], vertical_alignment="top")
    with overview_cols[0]:
        render_card(t("app.executive_brief", lang), investigation["executive_brief"])
        render_card(
            "What the copilot sees" if lang == "en" else "Ce que le copilote voit",
            html_bullets(detect_business_levers(profile, lang)[:3]),
        )
    with overview_cols[1]:
        render_card(
            "Suggested next moves" if lang == "en" else "Prochaines pistes suggerees",
            html_bullets([item["title"] for item in investigation["investigation_suggestions"][:3]]),
        )
        render_card(t("app.guardrail", lang), t("app.guardrail_body", lang))

    st.markdown(f"#### {'Portfolio and demo mode' if lang == 'en' else 'Mode portfolio et demo'}")
    cta_cols = st.columns(3)
    if cta_cols[0].button(t("landing.cta_sales", lang), use_container_width=True):
        load_named_sample("sales")
        run_guided_demo(st.session_state.dataset["dataset_id"])
        st.rerun()
    if cta_cols[1].button(t("landing.cta_marketing", lang), use_container_width=True):
        load_named_sample("marketing")
        st.rerun()
    if cta_cols[2].button(t("landing.cta_question", lang), use_container_width=True):
        example_question = "Should we increase price?" if lang == "en" else "Faut-il augmenter le prix ?"
        run_global_copilot_query(dataset_id, example_question, "revenue")

    portfolio_cols = st.columns(2, vertical_alignment="top")
    with portfolio_cols[0]:
        render_card(t("landing.offer", lang), (
            "<strong>Starter</strong>: diagnostics, insights, and guided investigation suggestions<br><br>"
            "<strong>Pro</strong>: prediction, scenario simulation, bilingual decision cockpit, and evidence pack<br><br>"
            "<strong>Advisory</strong>: premium onboarding, demo datasets, decision workflows, and executive reporting"
            if lang == "en"
            else "<strong>Starter</strong> : diagnostics, insights et suggestions d'investigation guidees<br><br>"
            "<strong>Pro</strong> : prediction, simulation de scenarios, cockpit de decision bilingue et pack de preuves<br><br>"
            "<strong>Advisory</strong> : onboarding premium, datasets de demo, workflows de decision et reporting executif"
        ))
    with portfolio_cols[1]:
        render_card(t("landing.pricing", lang), (
            "<strong>Starter</strong>: 79 EUR / month<br><strong>Pro</strong>: 249 EUR / month<br><strong>Advisory</strong>: custom pricing + onboarding"
            if lang == "en"
            else "<strong>Starter</strong> : 79 EUR / mois<br><strong>Pro</strong> : 249 EUR / mois<br><strong>Advisory</strong> : tarification sur mesure + onboarding"
        ))

with tabs[1]:
    st.markdown(f"### {t('investigation.suggestions', st.session_state.lang)}")
    for suggestion in investigation["investigation_suggestions"]:
        cols = st.columns([0.76, 0.24], vertical_alignment="center")
        with cols[0]:
            render_card(
                suggestion["title"],
                f"{suggestion['explanation']}<br><br><strong>{t('investigation.expected_impact', st.session_state.lang)}:</strong> {suggestion['expected_impact']}<br><strong>{t('investigation.confidence', st.session_state.lang)}:</strong> {suggestion.get('confidence_pct', 0)}%",
            )
        with cols[1]:
            if st.button(t("investigation.button", st.session_state.lang), key=f"invest_{suggestion['suggestion_id']}", use_container_width=True):
                payload = dict(suggestion["payload"])
                payload["investigation_type"] = suggestion["investigation_type"]
                st.session_state.focused_analysis = api_post(
                    "/investigate-path",
                    json={"dataset_id": dataset_id, "suggestion_id": suggestion["suggestion_id"], "payload": payload, "language": st.session_state.lang},
                )
    focused = st.session_state.get("focused_analysis")
    if focused:
        render_card(focused["title"], f"{focused['analysis']}<br><br><strong>{t('investigation.business_implication', st.session_state.lang)}:</strong> {focused['business_implication']}")
        st.json(focused["supporting_stats"])
        if focused.get("chart_spec"):
            st.plotly_chart(go.Figure(focused["chart_spec"]), use_container_width=True, key=f"focused_chart_{focused['title']}")

    st.markdown(f"### {t('investigation.ranked_insights', st.session_state.lang)}")
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
    render_card(t("investigation.opportunity_areas", st.session_state.lang), html_bullets(investigation["opportunity_areas"]))
    render_card(t("investigation.anomaly_narrative", st.session_state.lang), investigation["anomaly_narrative"])
    for chart_idx, chart_spec in enumerate(investigation["chart_specs"]):
        render_insight_panel(
            chart_spec["title"],
            chart_spec["insight"],
            chart_spec["why_it_matters"],
            chart_spec["impact_level"],
            chart_spec["confidence"],
            st.session_state.lang,
        )
        st.caption(chart_spec["question"])
        st.plotly_chart(go.Figure(chart_spec["figure"]), use_container_width=True, key=f"investigation_chart_{chart_idx}")

with tabs[2]:
    target_candidates = target_options
    selected_target = st.selectbox(t("prediction.choose_target", st.session_state.lang), target_candidates)
    if st.button(t("prediction.train_button", st.session_state.lang), type="primary"):
        st.session_state.training = api_post("/train", json={"dataset_id": dataset_id, "target": selected_target})
        st.session_state.actions = None
    training = st.session_state.get("training")
    if training:
        cols = st.columns([0.85, 1.15], vertical_alignment="top")
        with cols[0]:
            render_insight_panel(
                t("prediction.top_drivers", st.session_state.lang),
                t(
                    "prediction.insight_summary",
                    st.session_state.lang,
                    driver=training["top_drivers"][0] if training["top_drivers"] else t("app.not_available", st.session_state.lang),
                ),
                "This matters because the top-ranked drivers are the best place to pressure-test the model before acting on it."
                if st.session_state.lang == "en"
                else "Cela compte car les leviers les mieux classes sont le meilleur point de depart pour tester le modele avant d'agir.",
                "high" if training["top_drivers"] else "medium",
                training["confidence_level"],
                st.session_state.lang,
            )
            render_card(
                t("prediction.trained", st.session_state.lang),
                (
                    f"{t('prediction.model_type', st.session_state.lang)}: <strong>{training['task_type']}</strong><br>"
                    f"{t('prediction.model_name', st.session_state.lang)}: <strong>{training['model_name']}</strong><br>"
                    f"{t('prediction.primary_metric', st.session_state.lang)}: <strong>{training['primary_metric_name'].upper()} = {training['primary_metric_value']}</strong><br>"
                    f"{t('copilot.confidence', st.session_state.lang)}: <strong>{confidence_label(training['confidence_level'], st.session_state.lang)}</strong><br>"
                    f"{t('prediction.data_coverage', st.session_state.lang)}: <strong>{training['data_coverage_pct']}%</strong>"
                ),
            )
            render_card(t("prediction.top_features", st.session_state.lang), "<br>".join(f"{idx + 1}. {driver}" for idx, driver in enumerate(training["top_drivers"][:5])))
            st.json(training["metrics"])
            st.caption(t("prediction.baseline_comparison", st.session_state.lang))
            st.json(training["baseline_metrics"])
        with cols[1]:
            st.caption(t("prediction.annotation_caption", st.session_state.lang))
            st.plotly_chart(go.Figure(training["feature_importance_chart"]), use_container_width=True, key="prediction_feature_importance")
            st.dataframe(pd.DataFrame(training["feature_importance"][:5]), use_container_width=True, hide_index=True)
    else:
        st.info(t("prediction.empty", st.session_state.lang))

with tabs[3]:
    training = st.session_state.get("training")
    if not training:
        st.info(t("prediction.train_first", st.session_state.lang))
    else:
        simulation = st.session_state.get("simulation")
        if st.button("Run guided scenario" if lang == "en" else "Lancer le scenario guide", type="primary"):
            run_guided_demo(dataset_id)
            st.rerun()
        if simulation:
            sim_cols = st.columns(4)
            sim_cols[0].metric(t("decision_engine.before", lang), simulation["prediction_before"])
            sim_cols[1].metric(t("decision_engine.after", lang), simulation["prediction_after"])
            sim_cols[2].metric(t("decision_engine.delta", lang), simulation["delta"])
            sim_cols[3].metric(t("decision_engine.delta_pct", lang), simulation["delta_pct"] if simulation["delta_pct"] is not None else t("app.not_available", lang))
            render_card("Scenario impact" if lang == "en" else "Impact du scenario", simulation["impact_summary"])
            render_card(t("app.guardrail", lang), simulation["guardrail_note"])
            with st.expander("Simulation details" if lang == "en" else "Details de simulation", expanded=False):
                st.json(simulation["reference_row"])
                st.json(simulation["simulated_row"])
        else:
            render_card(
                "Quick simulation" if lang == "en" else "Simulation rapide",
                "Use the guided scenario to surface a before/after impact, then move to the Decision Engine for deeper comparison."
                if lang == "en"
                else "Utilisez le scenario guide pour obtenir un impact avant/apres, puis passez au moteur de decision pour une comparaison plus complete.",
            )

with tabs[4]:
    training = st.session_state.get("training")
    if not training:
        st.info(t("prediction.train_first", st.session_state.lang))
    else:
        lang = st.session_state.lang
        st.markdown(
            f"""
            <div class="hero" style="padding:1.35rem 1.6rem;">
                <div class="hero-kicker">{t("decision_engine.title", lang)}</div>
                <div style="font-size:1.15rem; color:#163828; font-weight:700; margin:.3rem 0 .55rem 0;">{t("decision_engine.subtitle", lang)}</div>
                <div class="meta">{t("decision_engine.core_card_caption", lang)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        baseline_mode = st.radio(
            t("decision_engine.baseline_mode", lang),
            options=["reference_row", "dataset_average"],
            format_func=lambda value: t("decision_engine.reference_row", lang) if value == "reference_row" else t("decision_engine.average_case", lang),
            horizontal=True,
        )
        reference_index = None
        if baseline_mode == "reference_row":
            reference_index = int(
                st.number_input(
                    t("decision_engine.reference_index", lang),
                    min_value=0,
                    max_value=max(0, dataset["rows"] - 1),
                    value=0,
                    step=1,
                )
            )

        meta_signature = (training["model_id"], baseline_mode, reference_index, lang)
        if st.session_state.get("decision_engine_meta_signature") != meta_signature:
            st.session_state.decision_engine_meta = api_post(
                "/decision-engine",
                json={
                    "dataset_id": dataset_id,
                    "model_id": training["model_id"],
                    "baseline_mode": baseline_mode,
                    "reference_index": reference_index,
                    "language": lang,
                    "scenario_a": {},
                    "scenario_b": {},
                },
            )
            st.session_state.decision_engine_meta_signature = meta_signature

        decision_meta = st.session_state.get("decision_engine_meta") or {}
        available_inputs = [item for item in decision_meta.get("available_inputs", []) if item.get("available", True)]
        unavailable_inputs = [item for item in decision_meta.get("available_inputs", []) if not item.get("available", True)]
        segment_controls = [item for item in available_inputs if item["key"] in {"segment_column", "segment_value"}]
        scenario_controls = [item for item in available_inputs if item["key"] not in {"segment_column", "segment_value"}]
        segment_column = None
        segment_value = None
        if segment_controls:
            selector_cols = st.columns(2)
            segment_column_control = next((item for item in segment_controls if item["key"] == "segment_column"), None)
            segment_value_control = next((item for item in segment_controls if item["key"] == "segment_value"), None)
            if segment_column_control:
                options = segment_column_control.get("options", [])
                default_index = options.index(segment_column_control["default_value"]) if segment_column_control.get("default_value") in options else 0
                with selector_cols[0]:
                    segment_column = st.selectbox(
                        t("decision_engine.segment_dimension", lang),
                        options,
                        index=default_index,
                    )
            if segment_value_control:
                options = segment_value_control.get("options", [])
                default_index = options.index(segment_value_control["default_value"]) if segment_value_control.get("default_value") in options else 0
                with selector_cols[1]:
                    segment_value = st.selectbox(
                        t("decision_engine.segment_value", lang),
                        options,
                        index=default_index,
                    )
        a_col, b_col = st.columns(2, vertical_alignment="top")
        scenario_a: dict[str, object] = {}
        scenario_b: dict[str, object] = {}

        with a_col:
            st.markdown(f"**{t('decision_engine.scenario_a', lang)}**")
            for control in scenario_controls:
                if control["control_type"] == "slider":
                    scenario_a[control["key"]] = st.slider(
                        f"A - {control['label']}",
                        min_value=float(control["min_value"]),
                        max_value=float(control["max_value"]),
                        value=float(control["default_value"]),
                    )
                else:
                    options = control.get("options", [])
                    default_index = options.index(control["default_value"]) if control.get("default_value") in options else 0
                    scenario_a[control["key"]] = st.selectbox(
                        f"A - {control['label']}",
                        options,
                        index=default_index,
                    )

        with b_col:
            st.markdown(f"**{t('decision_engine.scenario_b', lang)}**")
            for control in scenario_controls:
                if control["control_type"] == "slider":
                    scenario_b[control["key"]] = st.slider(
                        f"B - {control['label']}",
                        min_value=float(control["min_value"]),
                        max_value=float(control["max_value"]),
                        value=float(control["default_value"]),
                    )
                else:
                    options = control.get("options", [])
                    default_index = options.index(control["default_value"]) if control.get("default_value") in options else 0
                    scenario_b[control["key"]] = st.selectbox(
                        f"B - {control['label']}",
                        options,
                        index=default_index,
                        key=f"b_{control['key']}",
                    )

        if unavailable_inputs:
            render_card(
                t("decision_engine.unavailable_inputs", lang),
                "<br>".join(
                    f"{item['label']}: {item.get('reason', t('app.not_available', lang))}"
                    for item in unavailable_inputs
                ),
            )

        if st.button(t("decision_engine.run", lang), type="primary"):
            st.session_state.decision_engine = api_post(
                "/decision-engine",
                json={
                    "dataset_id": dataset_id,
                    "model_id": training["model_id"],
                    "baseline_mode": baseline_mode,
                    "reference_index": reference_index,
                    "segment_column": segment_column,
                    "segment_value": segment_value,
                    "language": lang,
                    "scenario_a": scenario_a,
                    "scenario_b": scenario_b,
                },
            )
            st.session_state.simulation = None
            st.session_state.actions = None

        decision = st.session_state.get("decision_engine")
        if decision:
            delta_pct_value = decision.get("delta_pct")
            scenario_impact = "high" if isinstance(delta_pct_value, (int, float)) and abs(delta_pct_value) >= 10 else "medium"
            metrics = st.columns(3)
            metrics[0].metric(t("decision_engine.winner", lang), humanize_decision_choice(decision["recommended_decision"], lang))
            metrics[1].metric(t("decision_engine.before", lang), decision["prediction_before"])
            metrics[2].metric(t("decision_engine.delta_pct", lang), decision["delta_pct"] if decision["delta_pct"] is not None else t("app.not_available", lang))
            render_insight_panel(
                t("decision_engine.recommended", lang),
                t("decision_engine.summary.recommend_template", lang, decision=humanize_decision_choice(decision["recommended_decision"], lang).lower()),
                "This matters because the decision engine converts multiple scenario outputs into a single action-oriented recommendation with guardrails."
                if lang == "en"
                else "Cela compte car le moteur de decision transforme plusieurs sorties de scenario en une recommandation actionnable avec des garde-fous.",
                scenario_impact,
                confidence_label(decision["confidence"]["level"], lang),
                lang,
            )
            st.markdown(f"### {t('decision_engine.scenario_comparison', lang)}")
            chart_specs = decision.get("chart_specs", [])
            for chart_idx, chart_spec in enumerate(chart_specs[:2]):
                st.caption(chart_spec["title"])
                st.plotly_chart(go.Figure(chart_spec["figure"]), use_container_width=True, key=f"decision_chart_{chart_idx}")
            if len(chart_specs) > 2:
                with st.expander("More decision charts" if lang == "en" else "Autres graphiques de decision", expanded=False):
                    for extra_idx, chart_spec in enumerate(chart_specs[2:], start=2):
                        st.caption(chart_spec["title"])
                        st.plotly_chart(go.Figure(chart_spec["figure"]), use_container_width=True, key=f"decision_chart_{extra_idx}")

            summary_cols = st.columns(2, vertical_alignment="top")
            with summary_cols[0]:
                render_card(t("decision_engine.recommended", lang), humanize_decision_choice(decision["recommended_decision"], lang))
                render_card(t("decision_engine.main_risk", lang), decision["main_risk"])
                render_card(t("decision_engine.robustness", lang), confidence_label(decision["robustness"], lang))
                render_card(t("decision_engine.guardrails", lang), "<br>".join(f"- {item}" for item in decision["guardrails"]))
                render_card(t("decision_engine.next_analysis", lang), decision["next_best_analysis"])
            with summary_cols[1]:
                render_card(
                    t("decision_engine.confidence", lang),
                    (
                        f"{t('decision_engine.level', lang)}: <strong>{confidence_label(decision['confidence']['level'], lang)}</strong><br>"
                        f"{t('decision_engine.model_reliability', lang)}: <strong>{decision['model_reliability']}</strong><br>"
                        f"{t('decision_engine.data_size', lang)}: <strong>{decision['data_size']}</strong><br>"
                        f"{t('decision_engine.row_coverage', lang)}: <strong>{decision['confidence']['row_coverage_pct']}%</strong><br>"
                        f"{decision['disclaimer']}"
                    ),
                )
                render_card(
                    t("decision_engine.simulation_basis", lang),
                    (
                        f"{t('decision_engine.before', lang)}: <strong>{decision['prediction_before']}</strong><br>"
                        f"{t('decision_engine.after', lang)}: <strong>{decision['prediction_after']}</strong><br>"
                        f"{t('decision_engine.delta', lang)}: <strong>{decision['delta']}</strong><br>"
                        f"{t('decision_engine.delta_pct', lang)}: <strong>{decision['delta_pct'] if decision['delta_pct'] is not None else t('app.not_available', lang)}</strong><br>"
                        f"{t('decision_engine.basis', lang)}: <strong>{decision['simulation_basis_used']}</strong>"
                    ),
                )
                render_card(t("decision_engine.supporting_evidence", lang), "<br>".join(f"- {item}" for item in decision["supporting_evidence"]))

            render_card(t("decision_engine.impact_views", lang), "<br>".join(f"<strong>{item['label']}</strong>: {item['insight']}" for item in decision["impact_views"]))
            render_card(t("decision_engine.missing_data", lang), "<br>".join(
                f"<strong>{item['dataset_name']}</strong><br>{item['why_it_matters']}<br><strong>{t('decision_engine.gain', lang)}:</strong> {item['what_it_improves']}<br><strong>{t('decision_engine.join_key', lang)}:</strong> {item['merge_hint']}"
                for item in decision["missing_useful_data"]
            ))

            st.markdown(f"### {t('decision_engine.actions', lang)}")
            for action in decision["recommended_actions"]:
                render_card(
                    action["title"],
                    f"{action['rationale']}<br><br><strong>{t('decision_engine.expected_effect', lang)}:</strong> {action['expected_effect']}<br><strong>{t('decision_engine.priority', lang)}:</strong> {priority_label(action['priority'], lang)}",
                )

with tabs[1]:
    root_metric = st.selectbox(t("root_cause.metric", st.session_state.lang), [col for col in profile["columns"] if col in profile["numeric_columns"]] or profile["columns"])
    if st.button(t("root_cause.button", st.session_state.lang), type="primary"):
        st.session_state.root_cause = api_post("/root-cause", json={"dataset_id": dataset_id, "metric": root_metric, "language": st.session_state.lang})
    root_cause = st.session_state.get("root_cause")
    if root_cause:
        lead_driver = root_cause["main_drivers"][0]["driver"] if root_cause["main_drivers"] else root_cause["metric"]
        render_insight_panel(
            t("root_cause.most_plausible_driver", st.session_state.lang),
            t("root_cause.insight_summary", st.session_state.lang, driver=lead_driver),
            "This matters because it gives the team a first hypothesis to validate before making broader changes."
            if st.session_state.lang == "en"
            else "Cela compte car cela donne a l'equipe une premiere hypothese a valider avant des changements plus larges.",
            "high",
            "medium",
            st.session_state.lang,
        )
        render_card(t("root_cause.why_title", st.session_state.lang), root_cause["explanation"])
        for driver in root_cause["main_drivers"]:
            render_card(driver["driver"], f"{driver['explanation']}<br><strong>{t('root_cause.impact', st.session_state.lang)}:</strong> {driver['impact_estimate']}")
        render_card(t("root_cause.evidence", st.session_state.lang), html_bullets(root_cause["evidence"]))
        if root_cause.get("chart_spec"):
            st.caption(t("root_cause.caption", st.session_state.lang))
            st.plotly_chart(go.Figure(root_cause["chart_spec"]), use_container_width=True, key=f"root_cause_chart_{root_metric}")

with tabs[5]:
    decision = st.session_state.get("decision_engine")
    if decision:
        render_card(t("decision_engine.supporting_evidence", lang), "<br>".join(f"- {item}" for item in decision["supporting_evidence"]))
        with st.expander(t("decision_engine.evidence_pack", lang), expanded=True):
            render_card(t("decision_engine.metrics", lang), "<br>".join(f"<strong>{key}</strong>: {value}" for key, value in decision["evidence_pack"]["supporting_metrics"].items()))
            render_card(t("decision_engine.top_variables", lang), html_bullets(decision["evidence_pack"]["top_variables"]))
            render_card(t("decision_engine.chart_references", lang), html_bullets(decision["evidence_pack"]["chart_references"]))
            render_card(t("decision_engine.assumptions", lang), html_bullets(decision["evidence_pack"]["scenario_assumptions"]))
            render_card(t("decision_engine.quality", lang), "<br>".join(f"- {item}" for item in decision["evidence_pack"]["quality_indicators"]))

with tabs[6]:
    if st.button(t("enrichment.button", st.session_state.lang), type="primary"):
        st.session_state.enrichment = api_post("/enrichment-suggestions", json={"dataset_id": dataset_id, "language": st.session_state.lang})
    enrichment = st.session_state.get("enrichment")
    if enrichment:
        with st.expander(t("tab.enrichment", st.session_state.lang), expanded=False):
            for item in enrichment["suggestions"]:
                render_card(
                    item["dataset_name"],
                    (
                        f"<strong>{t('enrichment.why', st.session_state.lang)}:</strong> {item['why_it_matters']}<br><br>"
                        f"<strong>{t('enrichment.how', st.session_state.lang)}:</strong> {item['integration_hint']}<br><br>"
                        f"<strong>{t('enrichment.value', st.session_state.lang)}:</strong> {item['expected_value']}"
                    ),
                )
    else:
        st.info(t("enrichment.empty", st.session_state.lang))

with tabs[6]:
    datasets_catalog = st.session_state.get("datasets_catalog", [])
    if len(datasets_catalog) < 2:
        st.info(t("merge.empty", st.session_state.lang))
    else:
        label_pairs = [f"{item['filename']} ({item['dataset_id'][:8]})" for item in datasets_catalog]
        mapping = {f"{item['filename']} ({item['dataset_id'][:8]})": item["dataset_id"] for item in datasets_catalog}
        left_label = st.selectbox(t("merge.left_dataset", st.session_state.lang), label_pairs, key="merge_left")
        right_options = [label for label in label_pairs if label != left_label]
        right_label = st.selectbox(t("merge.right_dataset", st.session_state.lang), right_options, key="merge_right")
        if st.button(t("merge.preview_button", st.session_state.lang), type="primary"):
            st.session_state.merge_preview = api_post(
                "/merge-preview",
                json={"left_dataset_id": mapping[left_label], "right_dataset_id": mapping[right_label]},
            )
        preview = st.session_state.get("merge_preview")
        if preview:
            render_card(t("merge.recommendation", st.session_state.lang), preview["explanation"])
            render_card(t("merge.business_value", st.session_state.lang), preview["business_value"])
            if preview.get("compatibility_warnings"):
                render_card(t("merge.warnings", st.session_state.lang), "<br>".join(f"- {item}" for item in preview["compatibility_warnings"]))
            render_card(
                t("merge.join_suggestion", st.session_state.lang),
                (
                    f"{t('merge.suggested_keys', st.session_state.lang)}: <strong>{', '.join(preview['suggested_join_keys']) or t('app.none', st.session_state.lang)}</strong><br>"
                    f"{t('merge.readiness', st.session_state.lang)}: <strong>{preview['merge_readiness']}</strong><br>"
                    f"{t('merge.overlap_rows', st.session_state.lang)}: <strong>{preview['estimated_overlap_rows']}</strong>"
                ),
            )
            if preview["preview"]:
                with st.expander("Merge preview" if lang == "en" else "Apercu de fusion", expanded=False):
                    st.dataframe(pd.DataFrame(preview["preview"]), use_container_width=True, hide_index=True)

with tabs[5]:
    question = st.text_area(t("app.top_question", st.session_state.lang), placeholder=t("app.top_question_placeholder", st.session_state.lang))
    default_copilot_target = "revenue" if "revenue" in target_options else target_options[0]
    copilot_target = st.selectbox(
        t("app.target_override", st.session_state.lang),
        target_options,
        index=target_options.index(default_copilot_target),
        key="copilot_target_override",
    )
    if st.button(t("copilot.ask_button", st.session_state.lang), type="primary") and question.strip():
        run_global_copilot_query(dataset_id, question, copilot_target)
    answer = st.session_state.get("copilot_answer")
    if answer:
        render_card(t("copilot.short_answer", st.session_state.lang), answer["answer"])
        reasoning_cols = st.columns(2, vertical_alignment="top")
        with reasoning_cols[0]:
            render_card(t("copilot.intent_label", st.session_state.lang), humanize_intent(answer["intent"], st.session_state.lang))
            render_card(
                t("copilot.pipeline", st.session_state.lang),
                "<br>".join(f"{step['step']}. {step['purpose']} ({step['tool_name']})" for step in answer["plan"]),
            )
            render_card(
                t("copilot.tools", st.session_state.lang),
                "<br>".join(f"- {tool['tool_name']}: {tool['output_summary']}" for tool in answer["tools_used"]),
            )
        with reasoning_cols[1]:
            render_card(t("copilot.key_drivers", st.session_state.lang), "<br>".join(f"- {item}" for item in answer["key_drivers"]))
            render_card(t("copilot.supporting_evidence", st.session_state.lang), "<br>".join(f"- {item}" for item in answer["supporting_evidence"]))
            render_card(t("copilot.confidence", st.session_state.lang), f"{confidence_label(answer['confidence_level'], st.session_state.lang)} ({answer['confidence_score']}/100)")
        meta_cols = st.columns(2, vertical_alignment="top")
        with meta_cols[0]:
            render_card(
                t("copilot.model_reliability", st.session_state.lang),
                answer.get("model_reliability") or t("copilot.no_model_signal", st.session_state.lang),
            )
        with meta_cols[1]:
            coverage_value = answer.get("data_coverage_pct")
            render_card(
                t("copilot.coverage_guardrail", st.session_state.lang),
                (
                    f"{t('copilot.data_coverage', st.session_state.lang)}: <strong>{coverage_value}%</strong><br><br>{answer['guardrail']}"
                    if coverage_value is not None
                    else answer["guardrail"]
                ),
            )
        if answer.get("simulation_result"):
            render_card(t("copilot.simulation_result", st.session_state.lang), answer["simulation_result"])
        render_card(t("copilot.recommended_actions", st.session_state.lang), "<br>".join(f"- {item}" for item in answer["recommended_actions"]))
        next_cols = st.columns(2, vertical_alignment="top")
        with next_cols[0]:
            render_card(
                t("copilot.next_investigation", st.session_state.lang),
                "<br>".join(f"- {item}" for item in answer["suggested_next_investigation"]) or t("copilot.no_next_investigation", st.session_state.lang),
            )
        with next_cols[1]:
            missing_data_items = answer["missing_useful_data"]
            if missing_data_items:
                for item in missing_data_items:
                    render_card(
                        item["dataset_name"],
                        (
                            f"<strong>{t('copilot.why_matters', st.session_state.lang)}:</strong> {item['why_it_matters']}<br><br>"
                            f"<strong>{t('copilot.what_improves', st.session_state.lang)}:</strong> {item['what_it_improves']}<br><br>"
                            f"<strong>{t('copilot.how_merge', st.session_state.lang)}:</strong> {item['merge_hint']}"
                        ),
                    )
            else:
                render_card(t("copilot.missing_data", st.session_state.lang), t("copilot.no_missing_data", st.session_state.lang))
        if answer["follow_up_questions"]:
            st.markdown(f"### {t('copilot.follow_up', st.session_state.lang)}")
            follow_cols = st.columns(len(answer["follow_up_questions"]))
            for idx, follow_up in enumerate(answer["follow_up_questions"]):
                if follow_cols[idx].button(follow_up, key=f"follow_{idx}"):
                    run_global_copilot_query(dataset_id, follow_up, copilot_target)

with tabs[5]:
    actions = ensure_actions(dataset_id)
    if st.button(t("summary.generate", st.session_state.lang), type="primary"):
        st.session_state.summary = api_post(
            "/summary",
            json={
                "dataset_id": dataset_id,
                "language": st.session_state.lang,
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
            render_card(t("summary.key_insights", st.session_state.lang), html_bullets(summary["key_findings"]))
            render_card(t("summary.drivers", st.session_state.lang), html_bullets(summary["main_drivers"]))
            render_card(t("summary.opportunities", st.session_state.lang), html_bullets(summary["opportunities"]))
        with cols[1]:
            render_card(t("summary.risks", st.session_state.lang), html_bullets(summary["risks"]))
            render_card(t("summary.recommendations", st.session_state.lang), html_bullets(summary["recommendations"]))
            render_card(t("summary.limitations", st.session_state.lang), html_bullets(summary["limitations"]))

        root_cause_payload = st.session_state.get("root_cause")
        export_ready = api_post(
            "/report/export",
            json={
                "dataset_id": dataset_id,
                "profile": st.session_state.profile,
                "investigation": st.session_state.investigation,
                "training": st.session_state.get("training"),
                "simulation": st.session_state.get("simulation"),
                "root_cause": root_cause_payload,
            },
        )
        st.session_state.report_export = export_ready
        st.download_button(
            label=t("summary.download", st.session_state.lang),
            data=export_ready["html_content"],
            file_name="ai-decision-copilot-report.html",
            mime="text/html",
            use_container_width=True,
        )
    st.markdown(f"### {t('summary.recommended_actions', st.session_state.lang)}")
    for item in actions["recommended_actions"]:
        render_card(f"{item['title']} [{priority_label(item['priority'], st.session_state.lang)}]", f"{item['rationale']}<br><br><strong>{t('decision_engine.expected_effect', st.session_state.lang)}:</strong> {item['expected_effect']}")

with tabs[6]:
    with st.expander("Data Reference" if lang == "en" else "Reference des donnees", expanded=False):
        st.dataframe(
            pd.DataFrame(
                {
                    t("diagnostic.column", lang): profile["columns"],
                    t("diagnostic.dtype", lang): [profile["dtypes"][col] for col in profile["columns"]],
                    t("diagnostic.missing_pct", lang): [profile["missing_pct"][col] for col in profile["columns"]],
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    with st.expander("Signals Created by the Copilot" if lang == "en" else "Signaux crees par le copilote", expanded=False):
        render_card(
            t("diagnostic.derived_features", lang),
            "<br>".join(
                f"<strong>{item['feature']}</strong>: {item['reason']}"
                for item in profile.get("derived_feature_details", [])
            ) or t("diagnostic.no_derived_features", lang),
        )
    with st.expander("Data confidence" if lang == "en" else "Confiance dans les donnees", expanded=False):
        profile_quality_card = build_data_quality_chart(profile, lang)
        render_insight_panel(
            profile_quality_card["title"],
            profile_quality_card["insight"],
            profile_quality_card["why_it_matters"],
            profile_quality_card["impact_level"],
            profile_quality_card["confidence"],
            lang,
        )
        st.plotly_chart(go.Figure(profile_quality_card["figure"]), use_container_width=True, key="data_quality_chart")
    with st.expander(t("app.dataset_preview", lang), expanded=False):
        render_dataset_preview(dataset)

st.caption(t("footer.disclaimer", st.session_state.lang))
