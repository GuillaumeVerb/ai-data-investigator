from __future__ import annotations

import json
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

RISK_RED = "#b44747"
WARN_ORANGE = "#d38336"
OPPORTUNITY_GREEN = "#2f6d49"
BASELINE_BLUE = "#3f6db4"
NEUTRAL_SLATE = "#607087"
GRID = "rgba(31, 38, 31, 0.08)"
PAPER_BG = "rgba(255,252,247,0.96)"
PLOT_BG = "rgba(255,252,247,0.82)"


def _json_safe_figure(fig: go.Figure) -> dict:
    return json.loads(json.dumps(fig.to_plotly_json(), cls=PlotlyJSONEncoder))


def _apply_premium_layout(fig: go.Figure, title: str, subtitle: Optional[str] = None) -> go.Figure:
    full_title = title if not subtitle else f"{title}<br><sup>{subtitle}</sup>"
    fig.update_layout(
        title={"text": full_title, "x": 0.03, "xanchor": "left"},
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin={"l": 60, "r": 30, "t": 80, "b": 55},
        font={"family": "Space Grotesk, sans-serif", "color": "#1f261f"},
        title_font={"size": 20, "color": "#163828"},
        xaxis={"showgrid": False, "zeroline": False, "linecolor": "rgba(31, 38, 31, 0.18)"},
        yaxis={"gridcolor": GRID, "zeroline": False, "linecolor": "rgba(31, 38, 31, 0.18)"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0.0},
    )
    return fig


def _chart_card(
    *,
    title: str,
    insight: str,
    why_it_matters: str,
    impact_level: str,
    confidence: str,
    fig: go.Figure,
    question: str,
) -> dict[str, Any]:
    return {
        "title": title,
        "question": question,
        "insight": insight,
        "why_it_matters": why_it_matters,
        "impact_level": impact_level,
        "confidence": confidence,
        "figure": _json_safe_figure(fig),
    }


def _find_time_column(df: pd.DataFrame) -> Optional[str]:
    datetime_columns = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    if datetime_columns:
        return datetime_columns[0]
    for column in df.columns:
        if "date" in column.lower() or "time" in column.lower():
            if pd.api.types.is_datetime64_any_dtype(df[column]):
                return column
    return None


def _find_primary_metric(df: pd.DataFrame) -> Optional[str]:
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_columns:
        return None
    if "revenue" in numeric_columns:
        return "revenue"
    return numeric_columns[0]


def _format_pct(value: float) -> str:
    return f"{value:.1f}%"


def build_data_quality_chart(profile: Dict[str, Any]) -> dict[str, Any]:
    missing_pct = profile["missing_pct"]
    ordered = (
        pd.Series(missing_pct)
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    ordered.columns = ["column", "missing_pct"]
    colors = [RISK_RED if value >= 20 else WARN_ORANGE if value >= 10 else BASELINE_BLUE for value in ordered["missing_pct"]]
    fig = go.Figure(
        data=[
            go.Bar(
                x=ordered["missing_pct"],
                y=ordered["column"],
                orientation="h",
                marker_color=colors,
                text=[_format_pct(float(value)) for value in ordered["missing_pct"]],
                textposition="outside",
            )
        ]
    )
    fig.update_xaxes(title="Missing values (%)")
    fig.update_yaxes(title="")
    fig = _apply_premium_layout(
        fig,
        "Data Quality Exposure",
        "Columns with the highest missing-data pressure appear first.",
    )
    if not ordered.empty:
        top_column = ordered.iloc[0]
        fig.add_annotation(
            x=float(top_column["missing_pct"]),
            y=str(top_column["column"]),
            text="Highest missing-value risk",
            showarrow=True,
            arrowcolor=RISK_RED,
            font={"color": RISK_RED},
            bgcolor="rgba(255,252,247,0.9)",
        )
    insight = (
        f"Data coverage is {profile['data_coverage_pct']}%, with the biggest risk concentrated in "
        f"{ordered.iloc[0]['column']}." if not ordered.empty else "No material missing-value risk was detected."
    )
    why = "This matters because missing-data concentration can reduce confidence, distort ranking logic, and weaken model reliability."
    impact = "high" if not ordered.empty and float(ordered.iloc[0]["missing_pct"]) >= 20 else "medium"
    confidence = "high"
    return _chart_card(
        title="Data Quality / Missing Values",
        insight=insight,
        why_it_matters=why,
        impact_level=impact,
        confidence=confidence,
        fig=fig,
        question="Where is data quality most likely to weaken the analysis?",
    )


def _build_trend_anomaly_chart(df: pd.DataFrame) -> Optional[dict[str, Any]]:
    time_col = _find_time_column(df)
    value_col = _find_primary_metric(df)
    if not time_col or not value_col:
        return None

    ordered = df[[time_col, value_col]].dropna().sort_values(time_col).copy()
    if ordered.empty:
        return None
    aggregated = ordered.groupby(time_col, dropna=False)[value_col].mean().reset_index()
    if len(aggregated) < 3:
        return None

    diffs = aggregated[value_col].diff().fillna(0)
    largest_drop_idx = int(diffs.idxmin())
    largest_jump_idx = int(diffs.idxmax())
    anomaly_threshold = aggregated[value_col].std(ddof=0) or 0
    center = aggregated[value_col].mean()
    anomaly_mask = (aggregated[value_col] - center).abs() > max(anomaly_threshold * 1.25, 0)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=aggregated[time_col],
            y=aggregated[value_col],
            mode="lines+markers",
            line={"color": BASELINE_BLUE, "width": 3},
            marker={"size": 7, "color": BASELINE_BLUE},
            name=value_col,
        )
    )
    if anomaly_mask.any():
        anomaly_points = aggregated.loc[anomaly_mask]
        fig.add_trace(
            go.Scatter(
                x=anomaly_points[time_col],
                y=anomaly_points[value_col],
                mode="markers",
                marker={"size": 12, "color": RISK_RED, "symbol": "diamond"},
                name="Anomalies",
            )
        )

    drop_row = aggregated.iloc[largest_drop_idx]
    jump_row = aggregated.iloc[largest_jump_idx]
    fig.add_annotation(
        x=drop_row[time_col],
        y=float(drop_row[value_col]),
        text="Revenue drop starts here" if value_col == "revenue" else "Sharp decline detected",
        showarrow=True,
        arrowcolor=RISK_RED,
        bgcolor="rgba(255,252,247,0.95)",
        font={"color": RISK_RED},
    )
    fig.add_annotation(
        x=jump_row[time_col],
        y=float(jump_row[value_col]),
        text="Strong rebound / peak",
        showarrow=True,
        arrowcolor=OPPORTUNITY_GREEN,
        bgcolor="rgba(255,252,247,0.95)",
        font={"color": OPPORTUNITY_GREEN},
    )
    fig = _apply_premium_layout(
        fig,
        f"{value_col.capitalize()} Trend With Turning Points",
        "Peaks, drops, and unusual periods are emphasized to speed diagnosis.",
    )
    pct_change = 0.0 if aggregated[value_col].iloc[0] == 0 else ((aggregated[value_col].iloc[-1] - aggregated[value_col].iloc[0]) / aggregated[value_col].iloc[0]) * 100
    insight = f"{value_col.capitalize()} changed by {_format_pct(float(pct_change))} across the observed period, with a clear downside break and rebound points."
    why = "This chart helps decision-makers see when performance changed, not just that it changed."
    impact = "high" if abs(pct_change) >= 10 else "medium"
    confidence = "high"
    return _chart_card(
        title="Trend Chart With Anomaly Highlights",
        insight=insight,
        why_it_matters=why,
        impact_level=impact,
        confidence=confidence,
        fig=fig,
        question="What changed over time, and where did the pattern break?",
    )


def _build_correlation_heatmap(df: pd.DataFrame) -> Optional[dict[str, Any]]:
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] < 2:
        return None
    corr = numeric_df.corr().round(2)
    upper = corr.abs().where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack().sort_values(ascending=False)
    strongest_pair = upper.index[0] if not upper.empty else None

    fig = go.Figure(
        data=[
            go.Heatmap(
                z=corr.values,
                x=corr.columns.tolist(),
                y=corr.index.tolist(),
                colorscale=[
                    [0.0, "#b44747"],
                    [0.5, "#f4ead8"],
                    [1.0, "#2f6d49"],
                ],
                zmin=-1,
                zmax=1,
                text=corr.values,
                texttemplate="%{text}",
                hovertemplate="%{x} vs %{y}: %{z}<extra></extra>",
            )
        ]
    )
    fig = _apply_premium_layout(
        fig,
        "Business Signal Correlation Map",
        "Darker green and red cells highlight the strongest positive and negative relationships.",
    )
    if strongest_pair:
        x_name, y_name = strongest_pair
        fig.add_annotation(
            x=x_name,
            y=y_name,
            text="Strongest signal",
            showarrow=False,
            font={"color": "#163828", "size": 12},
            bgcolor="rgba(255,252,247,0.95)",
            bordercolor=OPPORTUNITY_GREEN,
        )
        insight = f"The strongest statistical relationship appears between {x_name} and {y_name}."
    else:
        insight = "Several numeric variables move together, but no single relationship dominates."
    why = "This chart quickly surfaces which variables may deserve deeper business investigation, feature engineering, or simulation."
    return _chart_card(
        title="Correlation Heatmap",
        insight=insight,
        why_it_matters=why,
        impact_level="medium",
        confidence="medium",
        fig=fig,
        question="Which variables move together strongly enough to matter for decisions?",
    )


def _build_price_demand_chart(df: pd.DataFrame) -> Optional[dict[str, Any]]:
    if "price" not in df.columns:
        return None
    y_col = "units_sold" if "units_sold" in df.columns else "revenue" if "revenue" in df.columns else None
    if not y_col:
        return None

    clean = df[["price", y_col]].dropna().copy()
    if len(clean) < 3:
        return None
    clean["price_rank"] = clean["price"].rank(pct=True)
    clean["y_rank"] = clean[y_col].rank(pct=True)
    outlier_mask = (clean["price_rank"] > 0.85) & (clean["y_rank"] < 0.25)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=clean["price"],
            y=clean[y_col],
            mode="markers",
            marker={"size": 10, "color": BASELINE_BLUE, "opacity": 0.72},
            name="Observed records",
        )
    )
    if outlier_mask.any():
        highlighted = clean.loc[outlier_mask]
        fig.add_trace(
            go.Scatter(
                x=highlighted["price"],
                y=highlighted[y_col],
                mode="markers",
                marker={"size": 12, "color": RISK_RED, "symbol": "diamond"},
                name="High-price weak-response points",
            )
        )
        sample = highlighted.iloc[0]
        fig.add_annotation(
            x=float(sample["price"]),
            y=float(sample[y_col]),
            text="Price increase coincides with lower volume" if y_col == "units_sold" else "High-price weak revenue point",
            showarrow=True,
            arrowcolor=RISK_RED,
            bgcolor="rgba(255,252,247,0.95)",
            font={"color": RISK_RED},
        )

    fig = _apply_premium_layout(
        fig,
        f"Price vs {y_col.replace('_', ' ').title()}",
        "Outliers and potentially risky price-response observations are highlighted.",
    )
    corr = float(clean[["price", y_col]].corr().iloc[0, 1])
    insight = f"The measured relationship between price and {y_col} is {corr:.2f}, with unusual observations flagged where price is high and response is weak."
    why = "This view is designed for pricing conversations, not just exploration. It helps quickly spot elasticity risk and unusual exceptions."
    impact = "high" if abs(corr) >= 0.5 else "medium"
    return _chart_card(
        title="Price Sensitivity View",
        insight=insight,
        why_it_matters=why,
        impact_level=impact,
        confidence="medium",
        fig=fig,
        question=f"Does price appear to change {y_col.replace('_', ' ')} in a meaningful way?",
    )


def _build_segment_comparison_chart(df: pd.DataFrame) -> Optional[dict[str, Any]]:
    metric = _find_primary_metric(df)
    if not metric:
        return None
    categorical_columns = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns.tolist()
    if not categorical_columns:
        return None
    segment_col = "region" if "region" in categorical_columns else categorical_columns[0]
    grouped = df.groupby(segment_col, dropna=False)[metric].mean().reset_index().sort_values(by=metric, ascending=False).head(8)
    if len(grouped) < 2:
        return None

    colors = [OPPORTUNITY_GREEN] + [WARN_ORANGE] * max(0, len(grouped) - 2) + [RISK_RED]
    fig = go.Figure(
        data=[
            go.Bar(
                x=grouped[metric],
                y=grouped[segment_col].astype(str),
                orientation="h",
                marker_color=colors[: len(grouped)],
                text=[round(float(value), 2) for value in grouped[metric]],
                textposition="outside",
            )
        ]
    )
    fig = _apply_premium_layout(
        fig,
        f"{metric.capitalize()} by {segment_col.capitalize()}",
        "Best and worst performers are emphasized to support prioritization.",
    )
    best = grouped.iloc[0]
    worst = grouped.iloc[-1]
    fig.add_annotation(
        x=float(best[metric]),
        y=str(best[segment_col]),
        text="Best performer",
        showarrow=True,
        arrowcolor=OPPORTUNITY_GREEN,
        font={"color": OPPORTUNITY_GREEN},
        bgcolor="rgba(255,252,247,0.95)",
    )
    fig.add_annotation(
        x=float(worst[metric]),
        y=str(worst[segment_col]),
        text=f"{worst[segment_col]} underperforms",
        showarrow=True,
        arrowcolor=RISK_RED,
        font={"color": RISK_RED},
        bgcolor="rgba(255,252,247,0.95)",
    )
    gap = float(best[metric] - worst[metric])
    insight = f"{best[segment_col]} leads while {worst[segment_col]} trails, creating an average {metric} gap of {gap:.2f}."
    why = "Segment comparison turns broad performance noise into a prioritization conversation about where to protect, fix, or invest."
    return _chart_card(
        title="Segment Comparison",
        insight=insight,
        why_it_matters=why,
        impact_level="high",
        confidence="high",
        fig=fig,
        question="Which regions, products, or channels are outperforming or underperforming?",
    )


def build_chart_specs(df: pd.DataFrame) -> list[dict]:
    cards: list[dict] = []
    for builder in [
        _build_trend_anomaly_chart,
        _build_correlation_heatmap,
        _build_price_demand_chart,
        _build_segment_comparison_chart,
    ]:
        chart_card = builder(df)
        if chart_card:
            cards.append(chart_card)
    return cards[:5]


def build_feature_importance_chart(feature_importance: list[dict]) -> dict:
    if not feature_importance:
        fig = _apply_premium_layout(go.Figure(), "No Feature Importance Available")
        return _json_safe_figure(fig)

    top_items = list(reversed(feature_importance[:7]))
    fig = go.Figure(
        data=[
            go.Bar(
                x=[float(item["importance"]) for item in top_items],
                y=[str(item["feature"]).replace("num__", "").replace("cat__", "") for item in top_items],
                orientation="h",
                marker_color=[OPPORTUNITY_GREEN if idx == len(top_items) - 1 else BASELINE_BLUE for idx, _ in enumerate(top_items)],
                text=[round(float(item["importance"]), 3) for item in top_items],
                textposition="outside",
            )
        ]
    )
    top_driver = str(feature_importance[0]["feature"]).replace("num__", "").replace("cat__", "")
    fig = _apply_premium_layout(
        fig,
        "Ranked Model Drivers",
        "The highest-ranked features are easiest to explain and pressure-test with stakeholders.",
    )
    fig.add_annotation(
        x=float(feature_importance[0]["importance"]),
        y=top_driver,
        text="Primary driver",
        showarrow=True,
        arrowcolor=OPPORTUNITY_GREEN,
        font={"color": OPPORTUNITY_GREEN},
        bgcolor="rgba(255,252,247,0.95)",
    )
    return _json_safe_figure(fig)


def build_scenario_comparison_chart(labels: list[str], values: list[float], delta_pcts: Optional[list[Optional[float]]] = None) -> dict:
    colors = [BASELINE_BLUE, WARN_ORANGE, OPPORTUNITY_GREEN][: len(labels)]
    fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=values,
                marker_color=colors,
                text=[f"{value:.2f}" for value in values],
                textposition="outside",
            )
        ]
    )
    fig = _apply_premium_layout(
        fig,
        "Scenario Comparison",
        "Baseline and alternatives are displayed side-by-side for faster trade-off review.",
    )
    if delta_pcts:
        for idx, pct in enumerate(delta_pcts[1:], start=1):
            if pct is not None:
                fig.add_annotation(
                    x=labels[idx],
                    y=values[idx],
                    text=f"{pct:+.1f}%",
                    showarrow=False,
                    yshift=28,
                    font={"color": OPPORTUNITY_GREEN if pct >= 0 else RISK_RED, "size": 13},
                    bgcolor="rgba(255,252,247,0.95)",
                )
    return _json_safe_figure(fig)


def build_root_cause_driver_chart(drivers: list[dict[str, str]], metric: str) -> dict:
    if not drivers:
        return _json_safe_figure(_apply_premium_layout(go.Figure(), f"Root-Cause Drivers for {metric}"))

    y_labels = [driver["driver"] for driver in reversed(drivers)]
    scores = list(range(1, len(drivers) + 1))
    colors = [RISK_RED if "trend" in label.lower() else WARN_ORANGE if "segment" in label.lower() else BASELINE_BLUE for label in y_labels]
    fig = go.Figure(
        data=[
            go.Bar(
                x=scores,
                y=y_labels,
                orientation="h",
                marker_color=colors,
                text=[driver["impact_estimate"] for driver in reversed(drivers)],
                textposition="outside",
            )
        ]
    )
    fig = _apply_premium_layout(
        fig,
        f"Root-Cause Driver View For {metric}",
        "This chart ranks the most plausible contributors without claiming causality.",
    )
    fig.add_annotation(
        x=scores[-1],
        y=y_labels[-1],
        text="Strongest driver",
        showarrow=True,
        arrowcolor=RISK_RED,
        font={"color": RISK_RED},
        bgcolor="rgba(255,252,247,0.95)",
    )
    return _json_safe_figure(fig)
