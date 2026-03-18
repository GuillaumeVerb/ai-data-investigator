from __future__ import annotations

import json
from typing import Any, Dict, Optional

from openai import OpenAI

from app.core.config import get_settings
from app.core.schemas import SummaryResponse


def _client() -> Optional[OpenAI]:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    return OpenAI(api_key=settings.openai_api_key)


def _extract_text(response: Any) -> str:
    return getattr(response, "output_text", "").strip()


def _extract_json(response: Any) -> Dict[str, Any]:
    text = _extract_text(response)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found.")
    return json.loads(text[start : end + 1])


def _safe_completion(system_prompt: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    client = _client()
    settings = get_settings()
    if client is None:
        return None
    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=(
                f"{system_prompt}\nReturn valid JSON only.\n\n"
                f"Payload:\n{json.dumps(payload, default=str)}"
            ),
        )
        return _extract_json(response)
    except Exception:
        return None


def narrate_investigation(payload: Dict[str, Any]) -> Dict[str, Any]:
    insights = payload.get("insights", [])
    anomalies = payload.get("anomalies", [])
    executive_brief = (
        f"The investigation surfaced {len(insights)} prioritized signals and {len(anomalies)} anomalous records. "
        "The strongest patterns can now be translated into concrete commercial actions."
    )
    opportunity_areas = [
        "Investigate revenue movement by time period and segment mix.",
        "Pressure-test price elasticity before broad pricing changes.",
        "Review outlier records to separate risk from one-off opportunity.",
    ]
    anomaly_narrative = (
        f"{len(anomalies)} records were flagged as atypical. "
        "These should be reviewed as business leads rather than treated as confirmed incidents."
    )
    fallback = {
        "executive_brief": executive_brief,
        "opportunity_areas": opportunity_areas,
        "anomaly_narrative": anomaly_narrative,
    }
    response = _safe_completion(
        (
            "You are an analytics consultant. Return JSON with executive_brief, opportunity_areas, anomaly_narrative. "
            "Keep it concise and business-oriented."
        ),
        payload,
    )
    if not response:
        return fallback
    return {
        "executive_brief": response.get("executive_brief", fallback["executive_brief"]),
        "opportunity_areas": response.get("opportunity_areas", fallback["opportunity_areas"])[:3],
        "anomaly_narrative": response.get("anomaly_narrative", fallback["anomaly_narrative"]),
    }


def narrate_simulation(payload: Dict[str, Any]) -> Dict[str, str]:
    before = payload["prediction_before"]
    after = payload["prediction_after"]
    narrative = payload["narrative"]
    impact_summary = f"Baseline prediction moves from {before} to {after} under the modeled scenario."
    guardrail_note = "This is based on model behavior, not causal inference."
    fallback = {
        "narrative": narrative,
        "impact_summary": impact_summary,
        "guardrail_note": guardrail_note,
    }
    response = _safe_completion(
        (
            "You explain business scenarios. Return JSON with narrative, impact_summary, guardrail_note. "
            "Be concise, executive, and non-causal."
        ),
        payload,
    )
    if not response:
        return fallback
    return {
        "narrative": response.get("narrative", fallback["narrative"]),
        "impact_summary": response.get("impact_summary", fallback["impact_summary"]),
        "guardrail_note": response.get("guardrail_note", fallback["guardrail_note"]),
    }


def _fallback_summary(payload: Dict[str, Any]) -> SummaryResponse:
    investigation = payload["investigation"]
    training = payload.get("training")
    simulation = payload.get("simulation")
    actions = investigation.get("recommended_actions", [])
    insights = investigation.get("insights", [])

    headline = "AI Data Investigator Executive Summary"
    key_findings = [item["title"] for item in insights[:3]] or ["No major findings yet."]
    main_drivers = training.get("top_drivers", [])[:3] if training else []
    risks = [
        "Anomalies and segment divergence may signal operational friction or data quality issues.",
        "Predictions should not be interpreted as causal proof.",
        "Model confidence depends on the breadth and representativeness of current data.",
    ]
    opportunities = investigation.get("opportunity_areas", [])[:3]
    recommendations = [item["title"] for item in actions[:3]] or [
        "Focus commercial attention on the highest-ranked insight.",
        "Validate the strongest scenario with a controlled test.",
        "Review segment differences before applying blanket decisions.",
    ]
    limitations = [
        "This MVP uses baseline-ready modeling rather than full model benchmarking.",
        "Outputs reflect available data and may shift with new observations.",
        "Scenario simulation is directional guidance, not causal evidence.",
    ]
    executive_summary = investigation.get("executive_brief", "")
    if training:
        executive_summary += (
            f" The prediction engine trained a {training['model_name']} {training['task_type']} model with "
            f"{training['primary_metric_name']}={training['primary_metric_value']}."
        )
    if simulation:
        executive_summary += f" Latest scenario: {simulation.get('impact_summary', simulation['narrative'])}"

    return SummaryResponse(
        dataset_id=payload["dataset_id"],
        headline=headline,
        executive_summary=executive_summary.strip(),
        recommendations=recommendations,
        limitations=limitations,
        key_findings=key_findings,
        main_drivers=main_drivers,
        risks=risks,
        opportunities=opportunities,
    )


def generate_summary(payload: Dict[str, Any]) -> SummaryResponse:
    fallback = _fallback_summary(payload)
    response = _safe_completion(
        (
            "You are a consulting-firm analytics advisor. Return JSON with headline, executive_summary, "
            "recommendations, limitations, key_findings, main_drivers, risks, opportunities. "
            "Each list should have 3 concise items."
        ),
        payload,
    )
    if not response:
        return fallback
    return SummaryResponse(
        dataset_id=payload["dataset_id"],
        headline=response.get("headline", fallback.headline),
        executive_summary=response.get("executive_summary", fallback.executive_summary),
        recommendations=response.get("recommendations", fallback.recommendations)[:3],
        limitations=response.get("limitations", fallback.limitations)[:3],
        key_findings=response.get("key_findings", fallback.key_findings)[:3],
        main_drivers=response.get("main_drivers", fallback.main_drivers)[:3],
        risks=response.get("risks", fallback.risks)[:3],
        opportunities=response.get("opportunities", fallback.opportunities)[:3],
    )
