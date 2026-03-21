from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


def _add_feature(enriched: pd.DataFrame, details: List[Dict[str, str]], name: str, values: pd.Series, reason: str) -> None:
    enriched[name] = values
    details.append({"feature": name, "reason": reason})


def build_derived_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[Dict[str, str]]]:
    enriched = df.copy()
    details: List[Dict[str, str]] = []

    temporal_columns = enriched.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    if temporal_columns:
        dt_col = temporal_columns[0]
        dt = enriched[dt_col]
        _add_feature(enriched, details, f"{dt_col}_month", dt.dt.month, "Captures monthly seasonality and recurring demand patterns.")
        _add_feature(enriched, details, f"{dt_col}_weekday", dt.dt.day_name(), "Highlights weekday effects and operational timing differences.")
        _add_feature(enriched, details, f"{dt_col}_quarter", dt.dt.quarter, "Separates quarter-level commercial cycles and reporting periods.")
        _add_feature(
            enriched,
            details,
            f"{dt_col}_season",
            dt.dt.month.map({12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring", 6: "summer", 7: "summer", 8: "summer", 9: "autumn", 10: "autumn", 11: "autumn"}),
            "Approximates seasonal behavior to explain broad demand swings.",
        )
        _add_feature(enriched, details, f"{dt_col}_is_weekend", dt.dt.dayofweek >= 5, "Flags weekend behavior versus standard working days.")
        _add_feature(enriched, details, f"{dt_col}_trend_index", pd.Series(range(len(enriched)), index=enriched.index), "Creates a simple time trend to separate underlying drift from short-term variation.")

    if {"revenue", "marketing_spend"}.issubset(enriched.columns):
        _add_feature(
            enriched,
            details,
            "revenue_to_marketing_spend",
            enriched["revenue"] / enriched["marketing_spend"].replace(0, np.nan),
            "Measures how efficiently marketing spend translates into revenue.",
        )

    if {"price"}.issubset(enriched.columns):
        avg_price = enriched["price"].replace(0, np.nan).mean()
        if not np.isnan(avg_price) and avg_price != 0:
            _add_feature(
                enriched,
                details,
                "price_index",
                enriched["price"] / avg_price,
                "Shows whether a record is priced above or below the portfolio average.",
            )

    if {"price", "discount_pct"}.issubset(enriched.columns):
        _add_feature(
            enriched,
            details,
            "discount_effect",
            enriched["price"] * (enriched["discount_pct"] / 100.0),
            "Approximates discount pressure on realized pricing power.",
        )

    if {"revenue", "units_sold"}.issubset(enriched.columns):
        _add_feature(
            enriched,
            details,
            "average_order_indicator",
            enriched["revenue"] / enriched["units_sold"].replace(0, np.nan),
            "Approximates average realized value per sold unit.",
        )

    sort_reference = temporal_columns[0] if temporal_columns else None
    if sort_reference:
        sorted_index = enriched.sort_values(sort_reference).index
    else:
        sorted_index = enriched.index

    rolling_candidates = [column for column in ["revenue", "units_sold", "marketing_spend"] if column in enriched.columns]
    for column in rolling_candidates:
        ordered = enriched.loc[sorted_index, column]
        rolling_avg = ordered.rolling(window=3, min_periods=2).mean().reindex(enriched.index)
        growth = ordered.pct_change().replace([np.inf, -np.inf], np.nan).reindex(enriched.index)
        momentum = ordered.diff().reindex(enriched.index)
        _add_feature(enriched, details, f"{column}_rolling_avg_3", rolling_avg, f"Smooths short-term noise in {column} to surface the underlying trajectory.")
        _add_feature(enriched, details, f"{column}_growth_rate", growth, f"Measures period-over-period change in {column}.")
        _add_feature(enriched, details, f"{column}_momentum", momentum, f"Tracks whether {column} is accelerating or slowing down.")

    numeric_columns = enriched.select_dtypes(include=["number"]).columns.tolist()
    for column in numeric_columns:
        normalized_name = f"{column}_normalized"
        std = enriched[column].std(ddof=0)
        if std and not np.isnan(std):
            _add_feature(
                enriched,
                details,
                normalized_name,
                (enriched[column] - enriched[column].mean()) / std,
                f"Places {column} on a comparable scale for modeling and anomaly review.",
            )

    derived_features = [item["feature"] for item in details if item["feature"] in enriched.columns]
    deduped_details: List[Dict[str, str]] = []
    seen: set[str] = set()
    for item in details:
        if item["feature"] not in seen:
            deduped_details.append(item)
            seen.add(item["feature"])
    return enriched, derived_features, deduped_details
