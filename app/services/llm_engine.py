from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

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
    if not text:
        raise ValueError("Empty LLM response.")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in LLM response.")
    return json.loads(text[start : end + 1])


def _safe_completion(system_prompt: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    client = _client()
    settings = get_settings()
    if client is None:
        return None

    prompt = (
        f"{system_prompt}\n"
        "Return valid JSON only. Do not use markdown fences.\n\n"
        f"Payload:\n{json.dumps(payload, default=str)}"
    )
    try:
        response = client.responses.create(model=settings.openai_model, input=prompt)
        return _extract_json(response)
    except Exception:
        return None


def narrate_investigation(payload: Dict[str, Any]) -> Dict[str, Any]:
    insights = payload.get("insights", [])
    anomalies = payload.get("anomalies", [])
    key_stats = payload.get("key_stats", {})

    top_titles = [item["title"] for item in insights[:3]]
    executive_brief = (
        "The dataset already shows actionable structure. "
        f"Top signals: {', '.join(top_titles) if top_titles else 'no dominant pattern yet'}. "
        f"Anomalies detected: {len(anomalies)}."
    )
    opportunity_areas = [
        "Focus commercial actions on the strongest segment or driver surfaced by the investigation.",
        "Validate whether anomalies reflect operational issues, campaign outliers, or data-quality noise.",
        "Use the leading relationships to guide the first predictive target selection.",
    ]
    anomaly_narrative = (
        f"{len(anomalies)} anomalous records were surfaced using a statistical heuristic. "
        "They should be reviewed as leads, not as confirmed incidents."
    )

    fallback = {
        "executive_brief": executive_brief,
        "opportunity_areas": opportunity_areas,
        "anomaly_narrative": anomaly_narrative,
    }

    llm_payload = {
        "insights": insights,
        "anomalies_count": len(anomalies),
        "key_stats": key_stats,
    }
    response = _safe_completion(
        (
            "You are an AI analytics consultant. Rewrite the investigation in executive language. "
            "Return JSON with keys: executive_brief, opportunity_areas, anomaly_narrative. "
            "Keep opportunity_areas as an array of exactly 3 concise actions."
        ),
        llm_payload,
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
    delta = payload["delta"]
    delta_pct = payload.get("delta_pct")

    if isinstance(before, float) and isinstance(after, float):
        direction = "upside" if after >= before else "downside"
        impact_summary = (
            f"This scenario creates a modeled {direction} versus the baseline: "
            f"{before:.2f} to {after:.2f}, delta {delta}."
        )
    else:
        impact_summary = f"The simulated scenario changes the predicted state from {before} to {after}."

    guardrail_note = (
        "This output is directional guidance from the trained model. "
        "It is not causal evidence and should be validated with fresh business data."
    )
    narrative = payload["narrative"]

    fallback = {
        "narrative": narrative,
        "impact_summary": impact_summary if delta_pct is None else f"{impact_summary} Relative change: {delta_pct}%.",
        "guardrail_note": guardrail_note,
    }

    response = _safe_completion(
        (
            "You are an AI consultant explaining a what-if simulation to a business stakeholder. "
            "Return JSON with keys: narrative, impact_summary, guardrail_note. "
            "Keep the tone concise, credible, and non-causal."
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

    insights = investigation.get("insights", [])
    top_insight = insights[0]["title"] if insights else "No major insight detected"
    headline = "AI Data Investigator Executive Brief"
    recommendations = [
        "Prioritize the strongest segment or driver surfaced by the investigation step.",
        "Validate the predictive model with fresh data before operational use.",
        "Use the scenario engine to compare options, not to claim causal certainty.",
    ]
    limitations = [
        "Insights reflect statistical signals and should be reviewed with domain context.",
        "The MVP uses one baseline model at a time rather than full model benchmarking.",
        "Scenario outputs reflect model behavior on observed data, not guaranteed outcomes.",
    ]

    summary = (
        f"Main signal: {top_insight}. "
        f"Data quality score: {payload['profile']['quality_score']}/100. "
        f"Investigation brief: {investigation.get('executive_brief', '')} "
    )
    if training:
        summary += (
            f"A {training['model_name']} model was trained on '{training['target']}' "
            f"with metrics {training['metrics']} versus baseline {training['baseline_metrics']}. "
        )
    if simulation:
        summary += f"Simulation impact: {simulation.get('impact_summary', simulation['narrative'])}"

    return SummaryResponse(
        dataset_id=payload["dataset_id"],
        headline=headline,
        executive_summary=summary.strip(),
        recommendations=recommendations,
        limitations=limitations,
    )


def generate_summary(payload: Dict[str, Any]) -> SummaryResponse:
    fallback = _fallback_summary(payload)
    response = _safe_completion(
        (
            "You are an AI analytics consultant writing a board-ready summary. "
            "Return JSON with keys: headline, executive_summary, recommendations, limitations. "
            "Recommendations and limitations must each contain exactly 3 concise bullet items."
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
    )
