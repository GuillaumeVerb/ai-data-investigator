from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.core.config import get_settings
from app.core.schemas import SummaryResponse


def _fallback_summary(payload: dict[str, Any]) -> SummaryResponse:
    investigation = payload["investigation"]
    training = payload.get("training")
    simulation = payload.get("simulation")

    insights = investigation.get("insights", [])
    top_insight = insights[0]["title"] if insights else "No major insight detected"
    recommendations = [
        "Prioritize the strongest segment or driver surfaced by the investigation step.",
        "Validate the model against fresh business data before any operational rollout.",
        "Use scenario simulation as a decision-support tool, not as causal proof.",
    ]
    limitations = [
        "The MVP uses baseline-ready preprocessing and a single model family.",
        "Insights are statistical signals and should be reviewed with business context.",
        "Scenario outputs reflect observed patterns in the data, not guaranteed outcomes.",
    ]

    summary = (
        f"Dataset diagnostic completed successfully. Main signal: {top_insight}. "
        f"Quality score: {payload['profile']['quality_score']}/100. "
    )
    if training:
        summary += (
            f"A {training['model_name']} baseline was trained for target '{training['target']}' "
            f"with metrics {training['metrics']}. "
        )
    if simulation:
        summary += f"Simulation result: {simulation['narrative']}"

    return SummaryResponse(
        dataset_id=payload["dataset_id"],
        executive_summary=summary.strip(),
        recommendations=recommendations,
        limitations=limitations,
    )


def generate_summary(payload: dict[str, Any]) -> SummaryResponse:
    settings = get_settings()
    if not settings.openai_api_key:
        return _fallback_summary(payload)

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = (
        "You are a business-facing analytics consultant. Summarize the analysis with three recommendations "
        "and three limitations. Keep the tone concise and practical.\n\n"
        f"{payload}"
    )
    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=prompt,
        )
    except Exception:
        return _fallback_summary(payload)

    text = getattr(response, "output_text", "").strip()
    if not text:
        return _fallback_summary(payload)

    recommendations = [
        "Focus on the top signal highlighted in the summary.",
        "Review model quality with domain stakeholders before action.",
        "Track future runs to compare scenario outcomes over time.",
    ]
    limitations = [
        "Model output is not causal evidence.",
        "The MVP relies on one baseline model at a time.",
        "Data quality issues can materially change conclusions.",
    ]
    return SummaryResponse(
        dataset_id=payload["dataset_id"],
        executive_summary=text,
        recommendations=recommendations,
        limitations=limitations,
    )
