from __future__ import annotations

import numpy as np
import pandas as pd

from app.core.config import get_settings
from app.core.schemas import InsightItem, InvestigateResponse
from app.core.state import store
from app.services.charts import build_chart_specs
from app.services.llm_engine import narrate_investigation


def _top_correlation_insight(df: pd.DataFrame) -> InsightItem | None:
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] < 2:
        return None

    corr = numeric_df.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack().sort_values(ascending=False)
    if upper.empty:
        return None

    (left, right), score = upper.index[0], float(upper.iloc[0])
    severity = "high" if score >= 0.7 else "medium"
    return InsightItem(
        title=f"Strong relationship between {left} and {right}",
        description=f"The absolute correlation is {score:.2f}, which makes this pair useful for segmentation and prediction.",
        severity=severity,
        confidence=min(0.95, round(score, 2)),
    )


def _segment_insight(df: pd.DataFrame) -> InsightItem | None:
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns.tolist()
    if not numeric_columns or not categorical_columns:
        return None

    grouped = df.groupby(categorical_columns[0], dropna=False)[numeric_columns[0]].mean().sort_values(ascending=False)
    if grouped.empty:
        return None
    top_segment = grouped.index[0]
    top_value = grouped.iloc[0]

    return InsightItem(
        title=f"{top_segment} is the strongest segment on {numeric_columns[0]}",
        description=f"This segment leads with an average {numeric_columns[0]} of {top_value:.2f}, making it a strong candidate for targeted actions.",
        severity="medium",
        confidence=0.74,
    )


def _temporal_insight(df: pd.DataFrame) -> InsightItem | None:
    datetime_columns = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    if not datetime_columns or not numeric_columns:
        return None

    dt_col = datetime_columns[0]
    value_col = numeric_columns[0]
    ordered = df.sort_values(dt_col)
    recent_window = ordered.tail(max(3, len(ordered) // 4))
    early_window = ordered.head(max(3, len(ordered) // 4))
    delta = recent_window[value_col].mean() - early_window[value_col].mean()
    pct = 0.0 if early_window[value_col].mean() == 0 else (delta / early_window[value_col].mean()) * 100
    severity = "high" if abs(pct) >= 10 else "low"

    return InsightItem(
        title=f"Recent shift detected on {value_col}",
        description=f"The latest period differs by {delta:.2f} ({pct:.1f}%) versus the earliest period in the dataset.",
        severity=severity,
        confidence=0.7,
    )


def _detect_anomalies(df: pd.DataFrame) -> list[dict]:
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_columns:
        return []

    settings = get_settings()
    z_scores = (df[numeric_columns] - df[numeric_columns].mean()) / df[numeric_columns].std(ddof=0).replace(0, 1)
    anomaly_mask = z_scores.abs().max(axis=1) > max(2.0, 2.5 - settings.anomaly_contamination)
    anomalies = df.loc[anomaly_mask].head(5).copy()
    if anomalies.empty:
        return []

    anomalies = anomalies.astype(object).where(pd.notnull(anomalies), None)
    return anomalies.to_dict(orient="records")


def investigate_dataset(dataset_id: str) -> InvestigateResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe

    insight_candidates = [
        _top_correlation_insight(df),
        _segment_insight(df),
        _temporal_insight(df),
    ]
    insights = [item for item in insight_candidates if item is not None]

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    key_stats: dict[str, float | int] = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "numeric_columns": len(numeric_columns),
    }
    if numeric_columns:
        key_stats["avg_primary_metric"] = float(df[numeric_columns[0]].mean())

    anomalies = _detect_anomalies(df)
    narration = narrate_investigation(
        {
            "dataset_id": dataset_id,
            "insights": [item.model_dump() for item in insights[:5]],
            "anomalies": anomalies,
            "key_stats": key_stats,
        }
    )

    return InvestigateResponse(
        dataset_id=dataset_id,
        insights=insights[:5],
        anomalies=anomalies,
        key_stats=key_stats,
        chart_specs=build_chart_specs(df),
        executive_brief=narration["executive_brief"],
        opportunity_areas=narration["opportunity_areas"],
        anomaly_narrative=narration["anomaly_narrative"],
    )
