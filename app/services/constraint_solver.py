from __future__ import annotations

from typing import Any

from app.core.schemas import ConstraintSolveResponse
from app.core.state import store
from app.services.quant_optimizer import optimize_decision_levers
from app.services.scenario_engine import build_feature_frame, build_reference_row


def solve_with_constraints(
    dataset_id: str,
    model_id: str,
    objective: str = "maximize_prediction",
    language: str = "en",
) -> ConstraintSolveResponse:
    model_record = store.get_model(model_id)
    if model_record.dataset_id != dataset_id:
        raise ValueError("Model and dataset do not belong to the same analysis session.")

    optimized = optimize_decision_levers(dataset_id, model_id, objective, None, language)
    enriched_df, _ = build_feature_frame(dataset_id)
    base_row = build_reference_row(enriched_df, model_record.feature_columns)
    constrained_changes: dict[str, Any] = {}
    constraints_applied: list[str] = []

    for key, value in (optimized.recommended_changes or {}).items():
        base_value = base_row.get(key)
        if base_value is None:
            continue
        if key == "price":
            min_value = round(float(base_value) * 0.95, 2)
            max_value = round(float(base_value) * 1.1, 2)
            constrained_changes[key] = min(max(float(value), min_value), max_value)
            constraints_applied.append("price within -5% / +10% vs baseline")
        elif key == "marketing_spend":
            max_value = round(float(base_value) * 1.1, 2)
            constrained_changes[key] = min(float(value), max_value)
            constraints_applied.append("marketing spend increase capped at +10%")
        elif key in {"discount", "discount_pct"}:
            constrained_changes[key] = min(float(value), float(base_value) + 2)
            constraints_applied.append("discount increase capped at +2 points")
        else:
            constrained_changes[key] = value

    rationale = (
        "The constraint solver keeps the optimizer recommendation within business guardrails before rollout."
        if language == "en"
        else "Le constraint solver maintient la recommandation de l optimiseur dans des garde-fous business avant de deployer."
    )

    return ConstraintSolveResponse(
        dataset_id=dataset_id,
        model_id=model_id,
        objective=objective,
        recommended_changes=constrained_changes,
        constrained_prediction=optimized.optimized_prediction,
        constraints_applied=list(dict.fromkeys(constraints_applied)),
        rationale=rationale,
    )
