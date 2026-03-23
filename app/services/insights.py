from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from app.core.config import get_settings
from app.core.schemas import InsightItem, InvestigateResponse
from app.core.state import store
from app.services.action_engine import recommend_actions
from app.services.charts import build_chart_specs
from app.services.investigation_agent import build_investigation_suggestions
from app.services.llm_engine import narrate_investigation


def _build_insight(
    title: str,
    description: str,
    insight_type: str,
    signal_strength: float,
    business_relevance: float,
    data_coverage: float,
) -> InsightItem:
    rank_score = round(signal_strength * 0.45 + business_relevance * 0.35 + data_coverage * 0.20, 2)
    impact_level = "high" if rank_score >= 0.75 else "medium" if rank_score >= 0.45 else "low"
    icon = {"anomaly": "alert", "trend": "trend_up", "correlation": "hub"}.get(insight_type, "insight")
    return InsightItem(
        title=title,
        description=description,
        severity=impact_level,
        confidence=min(0.99, rank_score),
        impact_level=impact_level,
        confidence_pct=int(round(rank_score * 100)),
        insight_type=insight_type,  # type: ignore[arg-type]
        rank_score=rank_score,
        icon=icon,
    )


def _top_correlation_insight(df: pd.DataFrame, coverage: float, lang: str) -> Optional[InsightItem]:
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] < 2:
        return None

    corr = numeric_df.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack().sort_values(ascending=False)
    if upper.empty:
        return None

    (left, right), score = upper.index[0], float(upper.iloc[0])
    return _build_insight(
        title=(
            f"Strong correlation between {left} and {right}"
            if lang == "en"
            else f"Correlation forte entre {left} et {right}"
        ),
        description=(
            f"The absolute correlation is {score:.2f}, suggesting a meaningful relationship worth deeper analysis."
            if lang == "en"
            else f"La correlation absolue est de {score:.2f}, ce qui suggere une relation importante a analyser plus en profondeur."
        ),
        insight_type="correlation",
        signal_strength=min(1.0, score),
        business_relevance=0.84,
        data_coverage=coverage,
    )


def _segment_insight(df: pd.DataFrame, coverage: float, lang: str) -> Optional[InsightItem]:
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns.tolist()
    if not numeric_columns or not categorical_columns:
        return None

    grouped = df.groupby(categorical_columns[0], dropna=False)[numeric_columns[0]].mean().sort_values(ascending=False)
    if grouped.empty or len(grouped) < 2:
        return None

    top_segment = grouped.index[0]
    gap = float(grouped.iloc[0] - grouped.iloc[-1])
    normalized_gap = min(1.0, abs(gap) / max(1.0, abs(float(grouped.iloc[0]))))
    return _build_insight(
        title=f"{top_segment} behaves differently from the rest" if lang == "en" else f"{top_segment} se comporte differemment du reste",
        description=(
            f"Average {numeric_columns[0]} differs materially across {categorical_columns[0]} groups, with a top-to-bottom gap of {gap:.2f}."
            if lang == "en"
            else f"La moyenne de {numeric_columns[0]} differe nettement selon les groupes de {categorical_columns[0]}, avec un ecart de {gap:.2f} entre le haut et le bas."
        ),
        insight_type="trend",
        signal_strength=max(0.45, normalized_gap),
        business_relevance=0.76,
        data_coverage=coverage,
    )


def _temporal_insight(df: pd.DataFrame, coverage: float, lang: str) -> Optional[InsightItem]:
    datetime_columns = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    if not datetime_columns or not numeric_columns:
        return None

    dt_col = datetime_columns[0]
    value_col = "revenue" if "revenue" in numeric_columns else numeric_columns[0]
    ordered = df.sort_values(dt_col)
    recent_window = ordered.tail(max(3, len(ordered) // 4))
    early_window = ordered.head(max(3, len(ordered) // 4))
    early_mean = early_window[value_col].mean()
    recent_mean = recent_window[value_col].mean()
    pct = 0.0 if early_mean == 0 else ((recent_mean - early_mean) / early_mean) * 100
    return _build_insight(
        title=(
            f"{value_col.capitalize()} shifted across the observed period"
            if lang == "en"
            else f"{value_col.capitalize()} a evolue sur la periode observee"
        ),
        description=(
            f"The latest period differs by {pct:.1f}% versus the earliest period in the dataset."
            if lang == "en"
            else f"La periode la plus recente differe de {pct:.1f}% par rapport a la premiere periode du dataset."
        ),
        insight_type="trend",
        signal_strength=min(1.0, abs(pct) / 20),
        business_relevance=0.88,
        data_coverage=coverage,
    )


def _anomaly_insight(anomalies: List[Dict], coverage: float, lang: str) -> Optional[InsightItem]:
    if not anomalies:
        return None
    anomaly_share = len(anomalies) / max(len(anomalies), 5)
    return _build_insight(
        title="Anomalous rows require business review" if lang == "en" else "Les lignes atypiques demandent une revue business",
        description=(
            f"{len(anomalies)} unusual records were flagged and may reflect risks, exceptions, or data quality issues."
            if lang == "en"
            else f"{len(anomalies)} observations inhabituelles ont ete detectees et peuvent signaler des risques, exceptions ou problemes de qualite de donnees."
        ),
        insight_type="anomaly",
        signal_strength=min(1.0, anomaly_share),
        business_relevance=0.8,
        data_coverage=coverage,
    )


def _detect_anomalies(df: pd.DataFrame) -> List[Dict]:
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


def investigate_dataset(dataset_id: str, language: str = "en") -> InvestigateResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe
    lang = "fr" if language == "fr" else "en"
    anomalies = _detect_anomalies(df)
    coverage = max(0.0, 1.0 - float(df.isna().mean().mean()))

    insight_candidates = [
        _top_correlation_insight(df, coverage, lang),
        _segment_insight(df, coverage, lang),
        _temporal_insight(df, coverage, lang),
        _anomaly_insight(anomalies, coverage, lang),
    ]
    insights = [item for item in insight_candidates if item is not None]
    insights = sorted(insights, key=lambda item: item.rank_score, reverse=True)[:5]

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    key_stats: Dict[str, float | int] = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "numeric_columns": len(numeric_columns),
        "data_coverage_pct": round(coverage * 100, 1),
    }
    if numeric_columns:
        primary = "revenue" if "revenue" in numeric_columns else numeric_columns[0]
        key_stats["avg_primary_metric"] = float(df[primary].mean())

    suggestions = build_investigation_suggestions(df, lang)
    narration = narrate_investigation(
        {
            "dataset_id": dataset_id,
            "insights": [item.model_dump() for item in insights],
            "anomalies": anomalies,
            "key_stats": key_stats,
            "language": lang,
        }
    )
    actions = recommend_actions({"insights": [item.model_dump() for item in insights]}, lang=lang)

    return InvestigateResponse(
        dataset_id=dataset_id,
        insights=insights,
        investigation_suggestions=suggestions,
        anomalies=anomalies,
        key_stats=key_stats,
        chart_specs=build_chart_specs(df, lang),
        executive_brief=narration["executive_brief"],
        opportunity_areas=narration["opportunity_areas"],
        anomaly_narrative=narration["anomaly_narrative"],
        recommended_actions=actions,
    )
