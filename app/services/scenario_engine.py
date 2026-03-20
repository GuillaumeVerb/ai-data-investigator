from __future__ import annotations

import math
from typing import Any, Dict, Optional, Union

import pandas as pd

from app.core.schemas import SimulationResponse
from app.core.state import store
from app.services.feature_engineering import build_derived_features
from app.services.llm_engine import narrate_simulation


def _serialize_prediction(value: object) -> Union[float, str]:
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, (int, float)):
        return round(float(value), 4)
    return str(value)


def _apply_changes(base_row: pd.Series, changes: Dict[str, Any]) -> pd.Series:
    updated = base_row.copy()
    for key, value in changes.items():
        if key in updated.index:
            updated[key] = value
    return updated


def _resolve_discount_key(feature_columns: list[str]) -> Optional[str]:
    if "discount_pct" in feature_columns:
        return "discount_pct"
    if "discount" in feature_columns:
        return "discount"
    return None


def normalize_scenario_changes(changes: Optional[Dict[str, Any]], feature_columns: list[str]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}
    if not changes:
        return normalized

    discount_key = _resolve_discount_key(feature_columns)
    product_key = "product" if "product" in feature_columns else None

    for key, value in changes.items():
        resolved_key = key
        if key == "discount" and discount_key:
            resolved_key = discount_key
        elif key == "product_mix" and product_key:
            resolved_key = product_key
        if resolved_key in feature_columns:
            normalized[resolved_key] = value
    return normalized


def build_feature_frame(dataset_id: str) -> tuple[pd.DataFrame, Any]:
    dataset_record = store.get_dataset(dataset_id)
    enriched_df, _ = build_derived_features(dataset_record.dataframe.copy())
    return enriched_df, dataset_record


def build_reference_row(
    enriched_df: pd.DataFrame,
    feature_columns: list[str],
    baseline_mode: str = "reference_row",
    reference_index: Optional[int] = None,
) -> pd.Series:
    if baseline_mode == "dataset_average":
        base_values: Dict[str, Any] = {}
        for column in feature_columns:
            series = enriched_df[column]
            if pd.api.types.is_numeric_dtype(series):
                value = series.dropna().median() if not series.dropna().empty else 0.0
            else:
                modes = series.dropna().mode()
                value = modes.iloc[0] if not modes.empty else None
            base_values[column] = value
        return pd.Series(base_values, index=feature_columns, dtype=object)

    index = reference_index if reference_index is not None else 0
    if index >= len(enriched_df):
        raise ValueError("Reference index is out of bounds.")
    return enriched_df.iloc[index][feature_columns].copy()


def predict_row(model_id: str, row: pd.Series) -> Union[float, str]:
    model_record = store.get_model(model_id)
    frame = pd.DataFrame([row])
    return _serialize_prediction(model_record.pipeline.predict(frame)[0])


def row_coverage_pct(row: pd.Series) -> float:
    return round(float(100 - row.isna().mean() * 100), 1)


def _compute_delta(before: Union[float, str], after: Union[float, str]) -> tuple[Union[float, str], Optional[float], str]:
    if isinstance(before, float) and isinstance(after, float):
        delta_value = round(after - before, 4)
        delta_pct = None if math.isclose(before, 0.0) else round((delta_value / before) * 100, 2)
        direction = "increase" if delta_value >= 0 else "decrease"
        narrative = (
            f"The simulation suggests a {direction} of {abs(delta_value):.2f}"
            + (f" ({abs(delta_pct):.2f}%)." if delta_pct is not None else ".")
        )
        return delta_value, delta_pct, narrative
    return f"{before} -> {after}", None, f"The simulated scenario changes the predicted class from {before} to {after}."


def simulate_scenario(
    dataset_id: str,
    model_id: str,
    changes: Dict[str, Any],
    reference_index: Optional[int] = None,
    comparison_changes: Optional[Dict[str, Any]] = None,
) -> SimulationResponse:
    model_record = store.get_model(model_id)
    enriched_df, _dataset_record = build_feature_frame(dataset_id)

    if dataset_id != model_record.dataset_id:
        raise ValueError("Model and dataset do not belong to the same analysis session.")

    feature_columns = model_record.feature_columns
    base_row = build_reference_row(enriched_df, feature_columns, baseline_mode="reference_row", reference_index=reference_index)
    normalized_changes = normalize_scenario_changes(changes, feature_columns)
    scenario_row = _apply_changes(base_row, normalized_changes)

    before = predict_row(model_id, base_row)
    after = predict_row(model_id, scenario_row)
    delta, delta_pct, narrative = _compute_delta(before, after)

    comparison_prediction_after: Optional[Union[float, str]] = None
    comparison_delta: Optional[Union[float, str]] = None
    comparison_delta_pct: Optional[float] = None
    comparison_summary: Optional[str] = None
    comparison_row_dict: Optional[Dict[str, Any]] = None

    if comparison_changes:
        normalized_comparison_changes = normalize_scenario_changes(comparison_changes, feature_columns)
        comparison_row = _apply_changes(base_row, normalized_comparison_changes)
        comparison_prediction_after = predict_row(model_id, comparison_row)
        comparison_delta, comparison_delta_pct, _ = _compute_delta(before, comparison_prediction_after)
        comparison_row_dict = comparison_row.astype(object).where(pd.notnull(comparison_row), None).to_dict()
        comparison_summary = (
            f"Scenario B produces {comparison_prediction_after} versus baseline {before}, "
            f"for a delta of {comparison_delta}."
        )

    coverage = row_coverage_pct(base_row)
    confidence_level = "high" if coverage >= 90 else "medium" if coverage >= 75 else "low"

    narration = narrate_simulation(
        {
            "prediction_before": before,
            "prediction_after": after,
            "delta": delta,
            "delta_pct": delta_pct,
            "comparison_prediction_after": comparison_prediction_after,
            "comparison_delta": comparison_delta,
            "comparison_delta_pct": comparison_delta_pct,
            "narrative": narrative,
            "changes": normalized_changes,
            "comparison_changes": normalize_scenario_changes(comparison_changes, feature_columns) if comparison_changes else None,
            "target": model_record.target,
        }
    )

    base_row_dict = base_row.astype(object).where(pd.notnull(base_row), None).to_dict()
    scenario_row_dict = scenario_row.astype(object).where(pd.notnull(scenario_row), None).to_dict()

    return SimulationResponse(
        prediction_before=before,
        prediction_after=after,
        delta=delta,
        delta_pct=delta_pct,
        narrative=narration["narrative"],
        impact_summary=narration["impact_summary"],
        guardrail_note=narration["guardrail_note"],
        confidence_level=confidence_level,
        data_coverage_pct=coverage,
        comparison_prediction_after=comparison_prediction_after,
        comparison_delta=comparison_delta,
        comparison_delta_pct=comparison_delta_pct,
        comparison_summary=comparison_summary,
        reference_row=base_row_dict,
        simulated_row=scenario_row_dict,
        comparison_row=comparison_row_dict,
    )
