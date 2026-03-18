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
    dataset_record = store.get_dataset(dataset_id)
    model_record = store.get_model(model_id)
    df = dataset_record.dataframe.copy()
    enriched_df, _ = build_derived_features(df)

    if dataset_id != model_record.dataset_id:
        raise ValueError("Model and dataset do not belong to the same analysis session.")

    index = reference_index if reference_index is not None else 0
    if index >= len(enriched_df):
        raise ValueError("Reference index is out of bounds.")

    feature_columns = model_record.feature_columns
    base_row = enriched_df.iloc[index][feature_columns].copy()
    scenario_row = _apply_changes(base_row, changes)

    base_df = pd.DataFrame([base_row])
    scenario_df = pd.DataFrame([scenario_row])

    before = _serialize_prediction(model_record.pipeline.predict(base_df)[0])
    after = _serialize_prediction(model_record.pipeline.predict(scenario_df)[0])
    delta, delta_pct, narrative = _compute_delta(before, after)

    comparison_prediction_after: Optional[Union[float, str]] = None
    comparison_delta: Optional[Union[float, str]] = None
    comparison_delta_pct: Optional[float] = None
    comparison_summary: Optional[str] = None
    comparison_row_dict: Optional[Dict[str, Any]] = None

    if comparison_changes:
        comparison_row = _apply_changes(base_row, comparison_changes)
        comparison_df = pd.DataFrame([comparison_row])
        comparison_prediction_after = _serialize_prediction(model_record.pipeline.predict(comparison_df)[0])
        comparison_delta, comparison_delta_pct, _ = _compute_delta(before, comparison_prediction_after)
        comparison_row_dict = comparison_row.astype(object).where(pd.notnull(comparison_row), None).to_dict()
        comparison_summary = (
            f"Scenario B produces {comparison_prediction_after} versus baseline {before}, "
            f"for a delta of {comparison_delta}."
        )

    coverage = round(float(100 - enriched_df[feature_columns].isna().mean().mean() * 100), 1)
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
            "changes": changes,
            "comparison_changes": comparison_changes,
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
