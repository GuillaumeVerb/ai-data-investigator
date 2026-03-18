from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

import pandas as pd
import plotly.graph_objects as go

from app.core.schemas import InvestigationPathResponse, InvestigationSuggestion
from app.core.state import store
from app.services.charts import _json_safe_figure


def build_investigation_suggestions(df: pd.DataFrame) -> List[InvestigationSuggestion]:
    suggestions: List[InvestigationSuggestion] = []
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    datetime_columns = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns.tolist()

    if datetime_columns and "revenue" in df.columns:
        suggestions.append(
            InvestigationSuggestion(
                suggestion_id=str(uuid4()),
                title="Revenue trend changed over time",
                explanation="The dataset contains time structure and revenue, making post-period shifts worth reviewing.",
                investigation_type="trend",
                priority_score=0.91,
                payload={"value_column": "revenue", "date_column": datetime_columns[0]},
            )
        )

    if {"price", "units_sold"}.issubset(df.columns):
        suggestions.append(
            InvestigationSuggestion(
                suggestion_id=str(uuid4()),
                title="Strong relationship between price and units_sold",
                explanation="Price changes may be materially linked to sales volume and should be explored more deeply.",
                investigation_type="correlation",
                priority_score=0.88,
                payload={"left": "price", "right": "units_sold"},
            )
        )

    if "region" in df.columns and numeric_columns:
        suggestions.append(
            InvestigationSuggestion(
                suggestion_id=str(uuid4()),
                title="Some regions behave differently from the rest of the dataset",
                explanation="Regional divergence may reflect meaningful commercial opportunities or operational risks.",
                investigation_type="segment",
                priority_score=0.82,
                payload={"segment_column": "region", "value_column": numeric_columns[0]},
            )
        )

    if numeric_columns:
        suggestions.append(
            InvestigationSuggestion(
                suggestion_id=str(uuid4()),
                title="Outlier records may be driving a share of the performance story",
                explanation="A small number of extreme rows may explain a disproportionate amount of movement.",
                investigation_type="anomaly",
                priority_score=0.74,
                payload={"numeric_columns": numeric_columns[:5]},
            )
        )

    if categorical_columns and "revenue" in df.columns:
        suggestions.append(
            InvestigationSuggestion(
                suggestion_id=str(uuid4()),
                title="Channel or segment mix may explain revenue concentration",
                explanation="Comparing revenue by segment can reveal where performance is concentrated or diluted.",
                investigation_type="segment",
                priority_score=0.71,
                payload={"segment_column": categorical_columns[0], "value_column": "revenue"},
            )
        )

    return sorted(suggestions, key=lambda item: item.priority_score, reverse=True)[:5]


def investigate_path(dataset_id: str, suggestion_id: str, payload: Dict[str, Any]) -> InvestigationPathResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe
    inv_type = payload.get("investigation_type")

    if inv_type == "trend" or {"value_column", "date_column"}.issubset(payload):
        value_col = payload["value_column"]
        date_col = payload["date_column"]
        ordered = df.sort_values(date_col).copy()
        ordered["period"] = ordered[date_col].dt.to_period("M").astype(str)
        grouped = ordered.groupby("period", dropna=False)[value_col].mean().reset_index()
        change = grouped[value_col].iloc[-1] - grouped[value_col].iloc[0] if len(grouped) >= 2 else 0
        fig = go.Figure(data=[go.Scatter(x=grouped["period"], y=grouped[value_col], mode="lines+markers")])
        fig.update_layout(title=f"{value_col} over time", xaxis_title="period", yaxis_title=value_col)
        return InvestigationPathResponse(
            suggestion_id=suggestion_id,
            title="Focused trend investigation",
            analysis=f"{value_col} changes by {change:.2f} between the earliest and latest observed periods.",
            business_implication="Performance appears to shift over time, so decisions should compare recent versus historical behavior.",
            supporting_stats={"periods": int(len(grouped)), "delta": round(float(change), 2)},
            chart_spec=_json_safe_figure(fig),
        )

    if {"left", "right"}.issubset(payload):
        left = payload["left"]
        right = payload["right"]
        correlation = float(df[[left, right]].corr().iloc[0, 1])
        fig = go.Figure(data=[go.Scatter(x=df[left], y=df[right], mode="markers")])
        fig.update_layout(title=f"{left} vs {right}", xaxis_title=left, yaxis_title=right)
        return InvestigationPathResponse(
            suggestion_id=suggestion_id,
            title="Focused correlation investigation",
            analysis=f"The measured correlation between {left} and {right} is {correlation:.2f}.",
            business_implication="This relationship may indicate a pricing-response dynamic worth testing in a controlled way.",
            supporting_stats={"correlation": round(correlation, 2), "rows": int(len(df))},
            chart_spec=_json_safe_figure(fig),
        )

    if {"segment_column", "value_column"}.issubset(payload):
        segment_col = payload["segment_column"]
        value_col = payload["value_column"]
        grouped = (
            df.groupby(segment_col, dropna=False)[value_col].mean().reset_index().sort_values(by=value_col, ascending=False)
        )
        gap = grouped[value_col].iloc[0] - grouped[value_col].iloc[-1] if len(grouped) >= 2 else 0
        fig = go.Figure(data=[go.Bar(x=grouped[segment_col], y=grouped[value_col])])
        fig.update_layout(title=f"{value_col} by {segment_col}", xaxis_title=segment_col, yaxis_title=value_col)
        return InvestigationPathResponse(
            suggestion_id=suggestion_id,
            title="Focused segment investigation",
            analysis=f"The top segment outperforms the bottom segment by {gap:.2f} on average {value_col}.",
            business_implication="Segment performance is uneven, so broad strategies may be leaving value on the table.",
            supporting_stats={"segments": int(len(grouped)), "gap": round(float(gap), 2)},
            chart_spec=_json_safe_figure(fig),
        )

    numeric_columns = payload.get("numeric_columns", [])
    subset = df[numeric_columns].copy() if numeric_columns else df.select_dtypes(include=["number"]).copy()
    z_scores = (subset - subset.mean()) / subset.std(ddof=0).replace(0, 1)
    anomaly_count = int((z_scores.abs().max(axis=1) > 2.2).sum())
    return InvestigationPathResponse(
        suggestion_id=suggestion_id,
        title="Focused anomaly investigation",
        analysis=f"{anomaly_count} rows show unusually large deviations across the monitored numeric variables.",
        business_implication="Extreme observations may represent errors, special events, or operational edge cases.",
        supporting_stats={"anomaly_count": anomaly_count},
        chart_spec=None,
    )
