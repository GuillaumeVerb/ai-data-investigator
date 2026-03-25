from __future__ import annotations

import math
from typing import Any

from app.core.schemas import QuantOptimizeResponse
from app.core.state import store
from app.services.scenario_engine import build_feature_frame, build_reference_row, normalize_scenario_changes, predict_row


def _numeric_prediction(value: float | str) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def optimize_decision_levers(
    dataset_id: str,
    model_id: str,
    objective: str = "maximize_prediction",
    reference_index: int | None = None,
    language: str = "en",
) -> QuantOptimizeResponse:
    model_record = store.get_model(model_id)
    if model_record.dataset_id != dataset_id:
        raise ValueError("Model and dataset do not belong to the same analysis session.")

    enriched_df, _dataset_record = build_feature_frame(dataset_id)
    feature_columns = model_record.feature_columns
    base_row = build_reference_row(enriched_df, feature_columns, baseline_mode="reference_row", reference_index=reference_index)
    baseline_prediction = predict_row(model_id, base_row)
    baseline_numeric = _numeric_prediction(baseline_prediction)

    candidate_grid: list[dict[str, Any]] = []
    if "price" in feature_columns and base_row.get("price") is not None:
        base_price = float(base_row["price"])
        for multiplier in [0.95, 1.0, 1.05, 1.1]:
            candidate_grid.append({"price": round(base_price * multiplier, 2)})
    if "marketing_spend" in feature_columns and base_row.get("marketing_spend") is not None:
        base_spend = float(base_row["marketing_spend"])
        for multiplier in [0.95, 1.0, 1.05, 1.1, 1.15]:
            candidate_grid.append({"marketing_spend": round(base_spend * multiplier, 2)})
    discount_key = "discount_pct" if "discount_pct" in feature_columns else "discount" if "discount" in feature_columns else None
    if discount_key and base_row.get(discount_key) is not None:
        base_discount = float(base_row[discount_key])
        for delta in [-2, 0, 2]:
            candidate_grid.append({discount_key: max(0.0, round(base_discount + delta, 2))})

    combined_candidates: list[dict[str, Any]] = []
    price_candidates = [item for item in candidate_grid if "price" in item] or [{}]
    spend_candidates = [item for item in candidate_grid if "marketing_spend" in item] or [{}]
    discount_candidates = [item for item in candidate_grid if discount_key and discount_key in item] or [{}]
    for price_item in price_candidates:
        for spend_item in spend_candidates:
            for discount_item in discount_candidates:
                combo = {}
                combo.update(price_item)
                combo.update(spend_item)
                combo.update(discount_item)
                if combo:
                    combined_candidates.append(combo)

    best_changes: dict[str, Any] = {}
    best_prediction = baseline_prediction
    best_score = baseline_numeric if baseline_numeric is not None else -math.inf

    for changes in combined_candidates[:60]:
        normalized = normalize_scenario_changes(changes, feature_columns)
        scenario_row = base_row.copy()
        for key, value in normalized.items():
            scenario_row[key] = value
        predicted = predict_row(model_id, scenario_row)
        predicted_numeric = _numeric_prediction(predicted)
        if predicted_numeric is None:
            continue
        score = predicted_numeric
        if objective == "maximize_efficiency" and "marketing_spend" in normalized and normalized["marketing_spend"]:
            score = predicted_numeric / float(normalized["marketing_spend"])
        if best_score is None or score > best_score:
            best_score = score
            best_prediction = predicted
            best_changes = normalized

    if not best_changes:
        best_changes = {}

    baseline_numeric = _numeric_prediction(baseline_prediction)
    optimized_numeric = _numeric_prediction(best_prediction)
    if baseline_numeric is not None and optimized_numeric is not None:
        improvement: float | str = round(optimized_numeric - baseline_numeric, 4)
    else:
        improvement = f"{baseline_prediction} -> {best_prediction}"

    narrative = (
        f"The optimizer recommends {best_changes or 'keeping the baseline'} to improve the modeled outcome from {baseline_prediction} to {best_prediction}."
        if language == "en"
        else f"L optimiseur recommande {best_changes or 'de conserver la reference'} pour faire evoluer le resultat modele de {baseline_prediction} a {best_prediction}."
    )
    guardrails = [
        (
            "This optimizer is directional and should be reviewed with business constraints before rollout."
            if language == "en"
            else "Cet optimiseur est directionnel et doit etre revu avec les contraintes business avant de deployer."
        ),
        (
            "The search only tests a bounded set of scenarios around the reference row."
            if language == "en"
            else "La recherche ne teste qu un ensemble borne de scenarios autour de la ligne de reference."
        ),
    ]

    return QuantOptimizeResponse(
        dataset_id=dataset_id,
        model_id=model_id,
        objective=objective,
        recommended_changes=best_changes,
        baseline_prediction=baseline_prediction,
        optimized_prediction=best_prediction,
        improvement=improvement,
        tested_scenarios=len(combined_candidates[:60]),
        narrative=narrative,
        guardrails=guardrails,
    )
