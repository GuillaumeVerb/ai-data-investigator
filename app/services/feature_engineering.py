from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd


def build_derived_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    enriched = df.copy()
    derived_features: List[str] = []

    temporal_columns = enriched.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    if temporal_columns:
        dt_col = temporal_columns[0]
        enriched[f"{dt_col}_month"] = enriched[dt_col].dt.month
        enriched[f"{dt_col}_weekday"] = enriched[dt_col].dt.day_name()
        derived_features.extend([f"{dt_col}_month", f"{dt_col}_weekday"])

    if {"revenue", "marketing_spend"}.issubset(enriched.columns):
        ratio_col = "revenue_to_marketing_spend"
        enriched[ratio_col] = enriched["revenue"] / enriched["marketing_spend"].replace(0, np.nan)
        derived_features.append(ratio_col)

    numeric_columns = enriched.select_dtypes(include=["number"]).columns.tolist()
    for column in numeric_columns:
        normalized_name = f"{column}_normalized"
        std = enriched[column].std(ddof=0)
        if std and not np.isnan(std):
            enriched[normalized_name] = (enriched[column] - enriched[column].mean()) / std
            derived_features.append(normalized_name)

    return enriched, derived_features
