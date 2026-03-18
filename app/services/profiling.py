from __future__ import annotations

import pandas as pd

from app.core.schemas import ProfileResponse
from app.core.state import store


def _find_target_candidates(df: pd.DataFrame) -> list[str]:
    candidates: list[str] = []
    for column in df.columns:
        series = df[column]
        if pd.api.types.is_numeric_dtype(series) and series.nunique(dropna=True) > 5:
            candidates.append(column)
        elif series.nunique(dropna=True) in range(2, 8):
            candidates.append(column)
    return candidates[:5]


def build_profile(dataset_id: str) -> ProfileResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    temporal_columns = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    categorical_columns = [
        col for col in df.columns if col not in numeric_columns and col not in temporal_columns
    ]
    missing_pct = ((df.isna().mean() * 100).round(2)).to_dict()
    quality_score = round(max(0.0, 100 - float(df.isna().mean().mean() * 100) - len(df.columns) * 0.5), 1)

    headline_findings = [
        f"{df.shape[0]} rows and {df.shape[1]} columns available for analysis.",
        f"{len(numeric_columns)} numeric columns and {len(categorical_columns)} categorical columns detected.",
    ]
    if temporal_columns:
        headline_findings.append(f"Temporal signal detected in: {', '.join(temporal_columns[:2])}.")
    high_missing = [col for col, pct in missing_pct.items() if pct >= 20]
    if high_missing:
        headline_findings.append(f"Missing-value risk on: {', '.join(high_missing[:3])}.")
    else:
        headline_findings.append("Data quality looks healthy enough for a baseline model.")

    return ProfileResponse(
        dataset_id=dataset_id,
        shape={"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        columns=df.columns.tolist(),
        dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
        missing_pct=missing_pct,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        temporal_columns=temporal_columns,
        target_candidates=_find_target_candidates(df),
        quality_score=quality_score,
        headline_findings=headline_findings,
    )
