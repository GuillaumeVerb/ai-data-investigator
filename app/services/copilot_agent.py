from __future__ import annotations

from typing import Any, Dict, List

from app.core.schemas import CopilotAskResponse
from app.core.state import store
from app.services.action_engine import recommend_actions
from app.services.insights import investigate_dataset
from app.services.ml_engine import train_model
from app.services.root_cause import explain_root_cause
from app.services.scenario_engine import simulate_scenario


def _detect_intent(question: str) -> str:
    lower = question.lower()
    if any(token in lower for token in ["why", "drop", "decline", "cause"]):
        return "diagnosis"
    if any(token in lower for token in ["increase price", "should we", "what if", "scenario", "invest"]):
        return "simulation"
    if any(token in lower for token in ["predict", "forecast", "will"]):
        return "prediction"
    return "allocation"


def _pick_target(dataset_id: str, explicit_target: str | None) -> str:
    if explicit_target:
        return explicit_target
    record = store.get_dataset(dataset_id)
    if "revenue" in record.dataframe.columns:
        return "revenue"
    numeric = record.dataframe.select_dtypes(include=["number"]).columns.tolist()
    return numeric[0]


def answer_business_question(dataset_id: str, question: str, target: str | None = None, model_id: str | None = None) -> CopilotAskResponse:
    intent = _detect_intent(question)
    investigation = investigate_dataset(dataset_id)
    actions = recommend_actions({"insights": [item.model_dump() for item in investigation.insights]})
    training = None
    simulation = None
    evidence: List[str] = []
    key_drivers: List[str] = []

    if intent in {"prediction", "simulation", "allocation"}:
        selected_target = _pick_target(dataset_id, target)
        training = train_model(dataset_id, selected_target)
        key_drivers.extend(training.top_drivers[:3])
        evidence.append(f"Model {training.model_name} trained for {selected_target} with {training.primary_metric_name}={training.primary_metric_value}.")

    if intent == "simulation" and training:
        base_reference = training.reference_row
        changes: Dict[str, Any] = {}
        if "price" in base_reference:
            changes["price"] = float(base_reference["price"]) * 1.1
        if "marketing_spend" in base_reference:
            changes["marketing_spend"] = float(base_reference["marketing_spend"]) * 1.05
        if "discount_pct" in base_reference:
            changes["discount_pct"] = max(0.0, float(base_reference["discount_pct"]) - 1)
        simulation = simulate_scenario(dataset_id, training.model_id, changes)
        evidence.append(simulation.impact_summary)

    if intent == "diagnosis":
        metric = target or "revenue"
        root_cause = explain_root_cause(dataset_id, metric)
        key_drivers.extend([driver.driver for driver in root_cause.main_drivers[:3]])
        evidence.extend(root_cause.evidence[:3])
        answer = root_cause.explanation
        confidence_level = "medium"
    elif intent == "simulation" and training and simulation:
        answer = (
            f"A broad change is not automatically recommended. The current modeled scenario indicates: {simulation.impact_summary}"
        )
        confidence_level = simulation.confidence_level
    elif intent == "prediction" and training:
        answer = (
            f"The predictive model suggests that {training.target} is mainly driven by {', '.join(training.top_drivers[:3])}."
        )
        confidence_level = training.confidence_level
    else:
        answer = (
            "The current evidence suggests prioritizing the highest-ranked insights and validating targeted commercial actions before scaling."
        )
        confidence_level = "medium"

    if not key_drivers:
        key_drivers = [item.title for item in investigation.insights[:3]]
    if not evidence:
        evidence = [item.description for item in investigation.insights[:3]]

    return CopilotAskResponse(
        dataset_id=dataset_id,
        intent=intent,  # type: ignore[arg-type]
        answer=answer,
        key_drivers=key_drivers[:3],
        evidence=evidence[:4],
        simulation_result=simulation.impact_summary if simulation else None,
        confidence_level=confidence_level,  # type: ignore[arg-type]
        recommended_actions=[item.title for item in actions[:3]],
    )
