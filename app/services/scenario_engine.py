from __future__ import annotations

import math

import pandas as pd

from app.core.schemas import SimulationResponse
from app.core.state import store
from app.services.llm_engine import narrate_simulation


def _serialize_prediction(value: object) -> float | str:
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, (int, float)):
        return round(float(value), 4)
    return str(value)


def simulate_scenario(
    dataset_id: str,
    model_id: str,
    changes: dict[str, object],
    reference_index: int | None = None,
) -> SimulationResponse:
    dataset_record = store.get_dataset(dataset_id)
    model_record = store.get_model(model_id)
    df = dataset_record.dataframe.copy()

    if dataset_id != model_record.dataset_id:
        raise ValueError("Model and dataset do not belong to the same analysis session.")

    index = reference_index if reference_index is not None else 0
    if index >= len(df):
        raise ValueError("Reference index is out of bounds.")

    feature_columns = model_record.feature_columns
    base_row = df.iloc[index][feature_columns].copy()
    simulated_row = base_row.copy()

    for key, value in changes.items():
        if key in simulated_row.index:
            simulated_row[key] = value

    base_df = pd.DataFrame([base_row])
    simulated_df = pd.DataFrame([simulated_row])

    before_raw = model_record.pipeline.predict(base_df)[0]
    after_raw = model_record.pipeline.predict(simulated_df)[0]
    before = _serialize_prediction(before_raw)
    after = _serialize_prediction(after_raw)

    delta: float | str
    delta_pct: float | None = None
    if isinstance(before, float) and isinstance(after, float):
        delta_value = round(after - before, 4)
        delta = delta_value
        delta_pct = None if math.isclose(before, 0.0) else round((delta_value / before) * 100, 2)
        direction = "increase" if delta_value >= 0 else "decrease"
        narrative = (
            f"The simulation suggests a {direction} of {abs(delta_value):.2f}"
            + (f" ({abs(delta_pct):.2f}%)." if delta_pct is not None else ".")
        )
    else:
        delta = f"{before} -> {after}"
        narrative = f"The simulated scenario changes the predicted class from {before} to {after}."

    narration = narrate_simulation(
        {
            "prediction_before": before,
            "prediction_after": after,
            "delta": delta,
            "delta_pct": delta_pct,
            "narrative": narrative,
            "changes": changes,
            "reference_index": index,
            "target": model_record.target,
        }
    )

    base_row_dict = base_row.astype(object).where(pd.notnull(base_row), None).to_dict()
    simulated_row_dict = simulated_row.astype(object).where(pd.notnull(simulated_row), None).to_dict()

    return SimulationResponse(
        prediction_before=before,
        prediction_after=after,
        delta=delta,
        delta_pct=delta_pct,
        narrative=narration["narrative"],
        impact_summary=narration["impact_summary"],
        guardrail_note=narration["guardrail_note"],
        reference_row=base_row_dict,
        simulated_row=simulated_row_dict,
    )
