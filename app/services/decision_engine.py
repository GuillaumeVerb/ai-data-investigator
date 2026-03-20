from __future__ import annotations

import math
from typing import Any, Dict, Optional, Union

import pandas as pd

from app.core.schemas import (
    DecisionComparison,
    DecisionConfidence,
    DecisionEngineResponse,
    DecisionInputControl,
    DecisionScenarioComparison,
    DecisionScenarioRow,
)
from app.core.state import store
from app.services.action_engine import recommend_actions
from app.services.scenario_engine import (
    _apply_changes,
    _compute_delta,
    build_feature_frame,
    build_reference_row,
    normalize_scenario_changes,
    predict_row,
    row_coverage_pct,
)

DISCLAIMER = "This is based on model behavior and observed data patterns, not causal inference."
MATERIALITY_THRESHOLD_PCT = 2.0


def _serialize_row(row: pd.Series) -> Dict[str, Any]:
    return row.astype(object).where(pd.notnull(row), None).to_dict()


def _find_product_control(feature_columns: list[str], df: pd.DataFrame) -> Optional[DecisionInputControl]:
    if "product" in feature_columns:
        options = sorted(df["product"].dropna().astype(str).unique().tolist())
        return DecisionInputControl(
            key="product_mix",
            label="Product Mix",
            control_type="selectbox",
            default_value=options[0] if options else None,
            options=options,
        )

    product_share_columns = [column for column in feature_columns if "product_mix" in column or "share" in column]
    if product_share_columns:
        return DecisionInputControl(
            key=product_share_columns[0],
            label=product_share_columns[0].replace("_", " ").title(),
            control_type="slider",
            default_value=0.0,
            min_value=0.0,
            max_value=100.0,
        )

    return DecisionInputControl(
        key="product_mix",
        label="Product Mix",
        control_type="selectbox",
        available=False,
        reason="No product or product-share fields are available in the trained feature set.",
        options=[],
    )


def _build_available_inputs(base_row: pd.Series, feature_columns: list[str], df: pd.DataFrame) -> list[DecisionInputControl]:
    controls: list[DecisionInputControl] = []
    numeric_fields = {
        "price": "Price",
        "marketing_spend": "Marketing Spend",
    }
    discount_key = "discount_pct" if "discount_pct" in feature_columns else "discount" if "discount" in feature_columns else None
    if discount_key:
        numeric_fields[discount_key] = "Discount"

    for key, label in numeric_fields.items():
        if key in base_row.index and base_row[key] is not None:
            value = float(base_row[key])
            controls.append(
                DecisionInputControl(
                    key="discount" if key in {"discount", "discount_pct"} else key,
                    label=label,
                    control_type="slider",
                    min_value=round(value * 0.5, 2),
                    max_value=round(value * 1.5 + 1, 2),
                    default_value=value,
                )
            )

    if "region" in feature_columns:
        controls.append(
            DecisionInputControl(
                key="region",
                label="Region",
                control_type="selectbox",
                default_value=str(base_row.get("region")) if base_row.get("region") is not None else None,
                options=sorted(df["region"].dropna().astype(str).unique().tolist()),
            )
        )

    controls.append(_find_product_control(feature_columns, df))
    return controls


def _data_size_band(size: int) -> str:
    if size >= 500:
        return "large"
    if size >= 100:
        return "medium"
    return "small"


def _model_reliability_label(primary_metric_name: str, primary_metric_value: float) -> str:
    if primary_metric_name == "r2":
        if primary_metric_value >= 0.75:
            return "high"
        if primary_metric_value >= 0.5:
            return "medium"
        return "low"
    if primary_metric_value >= 0.8:
        return "high"
    if primary_metric_value >= 0.6:
        return "medium"
    return "low"


def _combined_confidence(model_reliability: str, row_coverage: float, data_size: str) -> str:
    score = {"low": 0, "medium": 1, "high": 2}[model_reliability]
    score += 2 if row_coverage >= 95 else 1 if row_coverage >= 80 else 0
    score += {"small": 0, "medium": 1, "large": 2}[data_size]
    if score >= 5:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


def _prediction_score(model_id: str, row: pd.Series) -> float:
    model_record = store.get_model(model_id)
    frame = pd.DataFrame([row])
    pipeline = model_record.pipeline
    if model_record.task_type == "classification" and hasattr(pipeline, "predict_proba"):
        probabilities = pipeline.predict_proba(frame)[0]
        return float(max(probabilities))
    prediction = predict_row(model_id, row)
    if isinstance(prediction, float):
        return prediction
    return 0.0


def _scenario_risk(changes: Dict[str, Any], row_coverage: float, model_reliability: str) -> str:
    if model_reliability == "low":
        return "Model reliability is low, so scenario ranking may not hold outside the current sample."
    if row_coverage < 85:
        return "The simulated row has limited coverage, which weakens confidence in the recommendation."
    if "price" in changes and "discount_pct" in changes:
        return "Price and discount moved together, which can hide true elasticity and margin trade-offs."
    if "price" in changes:
        return "A price change may reduce demand even if the model predicts a higher outcome."
    if "marketing_spend" in changes:
        return "Higher marketing spend can improve outcomes while still reducing efficiency if response saturates."
    if "region" in changes or "product" in changes:
        return "Segment or mix shifts may reflect allocation assumptions rather than directly achievable demand changes."
    return "The recommendation is directional and should be validated with a controlled business test."


def _next_best_analysis(changes: Dict[str, Any]) -> str:
    if "price" in changes:
        return "Run a price-sensitivity and segment elasticity review before rollout."
    if "marketing_spend" in changes:
        return "Compare marginal response by channel or region to confirm spend efficiency."
    if "region" in changes:
        return "Review segment comparison and root-cause evidence for the selected region."
    if "product" in changes or "product_mix" in changes:
        return "Inspect product-level margin and demand trade-offs before changing the mix."
    return "Review top model drivers and segment variance before acting on the scenario."


def _decision_summary(
    *,
    baseline_prediction: Union[float, str],
    scenario_a_prediction: Union[float, str],
    scenario_b_prediction: Optional[Union[float, str]],
    baseline_score: float,
    scenario_a_score: float,
    scenario_b_score: Optional[float],
    confidence_level: str,
    task_type: str,
) -> tuple[str, Union[float, str], Union[float, str], Union[float, str], Optional[float]]:
    winner = "scenario_a"
    winner_prediction = scenario_a_prediction
    winner_score = scenario_a_score
    if scenario_b_prediction is not None and scenario_b_score is not None and scenario_b_score > scenario_a_score:
        winner = "scenario_b"
        winner_prediction = scenario_b_prediction
        winner_score = scenario_b_score

    delta, delta_pct, _ = _compute_delta(baseline_prediction, winner_prediction)
    material = isinstance(delta_pct, float) and abs(delta_pct) >= MATERIALITY_THRESHOLD_PCT
    if task_type == "classification":
        material = not math.isclose(winner_score, baseline_score, rel_tol=0.0, abs_tol=0.02)

    if confidence_level == "low" or not material:
        return "baseline", baseline_prediction, baseline_prediction, 0.0 if isinstance(baseline_prediction, float) else f"{baseline_prediction} -> {baseline_prediction}", 0.0 if isinstance(baseline_prediction, float) else None

    return winner, baseline_prediction, winner_prediction, delta, delta_pct


def run_decision_engine(
    dataset_id: str,
    model_id: str,
    baseline_mode: str,
    scenario_a: Dict[str, Any],
    scenario_b: Optional[Dict[str, Any]] = None,
    reference_index: Optional[int] = None,
) -> DecisionEngineResponse:
    model_record = store.get_model(model_id)
    enriched_df, dataset_record = build_feature_frame(dataset_id)
    if dataset_id != model_record.dataset_id:
        raise ValueError("Model and dataset do not belong to the same analysis session.")

    feature_columns = model_record.feature_columns
    base_row = build_reference_row(enriched_df, feature_columns, baseline_mode=baseline_mode, reference_index=reference_index)
    available_inputs = _build_available_inputs(base_row, feature_columns, dataset_record.dataframe.copy())

    scenario_a_changes = normalize_scenario_changes(scenario_a, feature_columns)
    scenario_b_changes = normalize_scenario_changes(scenario_b, feature_columns) if scenario_b else None

    scenario_a_row = _apply_changes(base_row, scenario_a_changes)
    scenario_b_row = _apply_changes(base_row, scenario_b_changes) if scenario_b_changes else None

    baseline_prediction = predict_row(model_id, base_row)
    scenario_a_prediction = predict_row(model_id, scenario_a_row)
    scenario_b_prediction = predict_row(model_id, scenario_b_row) if scenario_b_row is not None else None

    baseline_score = _prediction_score(model_id, base_row)
    scenario_a_score = _prediction_score(model_id, scenario_a_row)
    scenario_b_score = _prediction_score(model_id, scenario_b_row) if scenario_b_row is not None else None

    row_coverage = min(
        row_coverage_pct(base_row),
        row_coverage_pct(scenario_a_row),
        row_coverage_pct(scenario_b_row) if scenario_b_row is not None else 100.0,
    )
    data_size = _data_size_band(len(enriched_df))
    model_reliability = _model_reliability_label(model_record.primary_metric_name, model_record.primary_metric_value)
    confidence_level = _combined_confidence(model_reliability, row_coverage, data_size)

    recommended_decision, prediction_before, prediction_after, delta, delta_pct = _decision_summary(
        baseline_prediction=baseline_prediction,
        scenario_a_prediction=scenario_a_prediction,
        scenario_b_prediction=scenario_b_prediction,
        baseline_score=baseline_score,
        scenario_a_score=scenario_a_score,
        scenario_b_score=scenario_b_score,
        confidence_level=confidence_level,
        task_type=model_record.task_type,
    )

    comparison_items = [
        DecisionScenarioComparison(
            scenario_key="baseline",
            prediction=baseline_prediction,
            delta=0.0 if isinstance(baseline_prediction, float) else f"{baseline_prediction} -> {baseline_prediction}",
            delta_pct=0.0 if isinstance(baseline_prediction, float) else None,
        ),
        DecisionScenarioComparison(
            scenario_key="scenario_a",
            prediction=scenario_a_prediction,
            delta=_compute_delta(baseline_prediction, scenario_a_prediction)[0],
            delta_pct=_compute_delta(baseline_prediction, scenario_a_prediction)[1],
        ),
    ]
    if scenario_b_prediction is not None:
        comparison_items.append(
            DecisionScenarioComparison(
                scenario_key="scenario_b",
                prediction=scenario_b_prediction,
                delta=_compute_delta(baseline_prediction, scenario_b_prediction)[0],
                delta_pct=_compute_delta(baseline_prediction, scenario_b_prediction)[1],
            )
        )

    winning_changes = {}
    if recommended_decision == "scenario_a":
        winning_changes = scenario_a_changes
    elif recommended_decision == "scenario_b" and scenario_b_changes:
        winning_changes = scenario_b_changes

    main_risk = _scenario_risk(winning_changes, row_coverage, model_reliability)
    next_best_analysis = _next_best_analysis(winning_changes or scenario_a_changes)
    confidence = DecisionConfidence(
        level=confidence_level,
        model_reliability=model_reliability,
        data_size=data_size,
        row_coverage_pct=row_coverage,
        disclaimer=DISCLAIMER,
    )

    recommended_actions = recommend_actions(
        investigation={"insights": []},
        training={
            "top_drivers": model_record.top_drivers,
            "confidence_level": model_record.confidence_level,
        },
        simulation={
            "delta_pct": delta_pct,
            "scenario_a_changes": scenario_a_changes,
            "scenario_b_changes": scenario_b_changes,
            "recommended_decision": recommended_decision,
            "main_risk": main_risk,
        },
    )

    return DecisionEngineResponse(
        baseline_prediction=baseline_prediction,
        scenario_a_prediction=scenario_a_prediction,
        scenario_b_prediction=scenario_b_prediction,
        prediction_before=prediction_before,
        prediction_after=prediction_after,
        delta=delta,
        delta_pct=delta_pct,
        comparison=DecisionComparison(winner=recommended_decision, scenarios=comparison_items),
        recommended_decision=recommended_decision,
        main_risk=main_risk,
        confidence=confidence,
        next_best_analysis=next_best_analysis,
        model_reliability=model_reliability,
        data_size=data_size,
        disclaimer=DISCLAIMER,
        available_inputs=available_inputs,
        scenario_rows=DecisionScenarioRow(
            baseline=_serialize_row(base_row),
            scenario_a=_serialize_row(scenario_a_row),
            scenario_b=_serialize_row(scenario_b_row) if scenario_b_row is not None else None,
        ),
        recommended_actions=recommended_actions,
    )
