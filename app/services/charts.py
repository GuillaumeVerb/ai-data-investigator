from __future__ import annotations

import json
import re
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


def _clean_feature_name(value: str) -> str:
    return str(value).replace("num__", "").replace("cat__", "").replace("_", " ")


def _parse_magnitude(value: object) -> float:
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return abs(float(match.group(0))) if match else 0.0


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


def _format_value(value: float) -> str:
    return f"{value:,.2f}" if abs(value) >= 100 else f"{value:.2f}"


def build_data_quality_chart(profile: Dict[str, Any], lang: str = "en", *_args: Any, **_kwargs: Any) -> dict[str, Any]:
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
    fig.update_xaxes(title="Missing values (%)" if lang == "en" else "Valeurs manquantes (%)")
    fig.update_yaxes(title="")
    fig = _apply_premium_layout(
        fig,
        "Data Quality Exposure" if lang == "en" else "Exposition a la qualite des donnees",
        "Columns with the highest missing-data pressure appear first." if lang == "en" else "Les colonnes les plus touchees par les donnees manquantes apparaissent en premier.",
    )
    if not ordered.empty:
        top_column = ordered.iloc[0]
        fig.add_annotation(
            x=float(top_column["missing_pct"]),
            y=str(top_column["column"]),
            text="Coverage risk concentrates here" if lang == "en" else "Le risque de couverture se concentre ici",
            showarrow=True,
            arrowcolor=RISK_RED,
            font={"color": RISK_RED},
            bgcolor="rgba(255,252,247,0.9)",
        )
        if len(ordered) > 1:
            second = ordered.iloc[1]
            fig.add_annotation(
                x=float(second["missing_pct"]),
                y=str(second["column"]),
                text="Next cleanup priority" if lang == "en" else "Priorite de nettoyage suivante",
                showarrow=True,
                arrowcolor=BASELINE_BLUE,
                font={"color": BASELINE_BLUE},
                bgcolor="rgba(255,252,247,0.9)",
                ax=35,
                ay=-25,
            )
    insight = (
        (
            f"Data coverage is {profile['data_coverage_pct']}%, with the biggest risk concentrated in {ordered.iloc[0]['column']}."
            if lang == "en"
            else f"La couverture des donnees est de {profile['data_coverage_pct']}%, avec le principal risque concentre sur {ordered.iloc[0]['column']}."
        )
        if not ordered.empty
        else ("No material missing-value risk was detected." if lang == "en" else "Aucun risque material de valeurs manquantes n'a ete detecte.")
    )
    why = (
        "This matters because missing-data concentration can reduce confidence, distort ranking logic, and weaken model reliability."
        if lang == "en"
        else "Cela compte car une forte concentration de valeurs manquantes peut reduire la confiance, biaiser la priorisation et affaiblir la fiabilite du modele."
    )
    impact = "high" if not ordered.empty and float(ordered.iloc[0]["missing_pct"]) >= 20 else "medium"
    confidence = "high"
    return _chart_card(
        title="Data Quality / Missing Values" if lang == "en" else "Qualite des donnees / Valeurs manquantes",
        insight=insight,
        why_it_matters=why,
        impact_level=impact,
        confidence=confidence,
        fig=fig,
        question="Where is data quality most likely to weaken the analysis?" if lang == "en" else "Ou la qualite des donnees risque-t-elle le plus d'affaiblir l'analyse ?",
    )


def _build_trend_anomaly_chart(df: pd.DataFrame, lang: str = "en") -> Optional[dict[str, Any]]:
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
                name="Anomalies" if lang == "en" else "Anomalies",
            )
        )
        first_anomaly = anomaly_points.iloc[0]
        fig.add_annotation(
            x=first_anomaly[time_col],
            y=float(first_anomaly[value_col]),
            text="Anomaly detected" if lang == "en" else "Anomalie detectee",
            showarrow=True,
            arrowcolor=RISK_RED,
            bgcolor="rgba(255,252,247,0.95)",
            font={"color": RISK_RED},
            ay=-45,
        )

    drop_row = aggregated.iloc[largest_drop_idx]
    jump_row = aggregated.iloc[largest_jump_idx]
    fig.add_annotation(
        x=drop_row[time_col],
        y=float(drop_row[value_col]),
        text=("Revenue drop starts here" if value_col == "revenue" else "Sharp decline detected") if lang == "en" else ("La baisse du revenu commence ici" if value_col == "revenue" else "Baisse nette detectee"),
        showarrow=True,
        arrowcolor=RISK_RED,
        bgcolor="rgba(255,252,247,0.95)",
        font={"color": RISK_RED},
    )
    fig.add_annotation(
        x=jump_row[time_col],
        y=float(jump_row[value_col]),
        text="Strong rebound / peak" if lang == "en" else "Fort rebond / pic",
        showarrow=True,
        arrowcolor=OPPORTUNITY_GREEN,
        bgcolor="rgba(255,252,247,0.95)",
        font={"color": OPPORTUNITY_GREEN},
    )
    fig = _apply_premium_layout(
        fig,
        f"{value_col.capitalize()} Trend With Turning Points" if lang == "en" else f"Tendance de {value_col} avec points de rupture",
        "Peaks, drops, and unusual periods are emphasized to speed diagnosis." if lang == "en" else "Les pics, baisses et periodes inhabituelles sont mis en avant pour accelerer le diagnostic.",
    )
    fig.add_vline(
        x=drop_row[time_col],
        line_dash="dot",
        line_color=RISK_RED,
        opacity=0.45,
    )
    pct_change = 0.0 if aggregated[value_col].iloc[0] == 0 else ((aggregated[value_col].iloc[-1] - aggregated[value_col].iloc[0]) / aggregated[value_col].iloc[0]) * 100
    insight = (
        f"{value_col.capitalize()} changed by {_format_pct(float(pct_change))} across the observed period, with a clear downside break and rebound points."
        if lang == "en"
        else f"{value_col.capitalize()} a evolue de {_format_pct(float(pct_change))} sur la periode observee, avec une rupture baissiere et des points de rebond visibles."
    )
    why = "This chart helps decision-makers see when performance changed, not just that it changed." if lang == "en" else "Ce graphique aide a voir quand la performance a change, pas seulement qu'elle a change."
    impact = "high" if abs(pct_change) >= 10 else "medium"
    confidence = "high"
    return _chart_card(
        title="Trend Chart With Anomaly Highlights" if lang == "en" else "Courbe de tendance avec anomalies",
        insight=insight,
        why_it_matters=why,
        impact_level=impact,
        confidence=confidence,
        fig=fig,
        question="What changed over time, and where did the pattern break?" if lang == "en" else "Qu'est-ce qui a change dans le temps, et ou le motif s'est-il rompu ?",
    )


def _build_correlation_heatmap(df: pd.DataFrame, lang: str = "en") -> Optional[dict[str, Any]]:
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] < 2:
        return None
    corr = numeric_df.corr().round(2)
    upper = corr.abs().where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack().sort_values(ascending=False)
    strongest_pair = upper.index[0] if not upper.empty else None
    upper_signed = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack().sort_values()
    strongest_negative = upper_signed.index[0] if not upper_signed.empty else None
    strongest_positive = upper_signed.index[-1] if not upper_signed.empty else None

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
        "Business Signal Correlation Map" if lang == "en" else "Carte de correlation des signaux business",
        "Darker green and red cells highlight the strongest positive and negative relationships." if lang == "en" else "Les cellules vertes et rouges les plus marquees soulignent les relations positives et negatives les plus fortes.",
    )
    if strongest_pair:
        x_name, y_name = strongest_pair
        fig.add_annotation(
            x=x_name,
            y=y_name,
            text="Strongest overall signal" if lang == "en" else "Signal global le plus fort",
            showarrow=False,
            font={"color": "#163828", "size": 12},
            bgcolor="rgba(255,252,247,0.95)",
            bordercolor=OPPORTUNITY_GREEN,
        )
        insight = f"The strongest statistical relationship appears between {x_name} and {y_name}." if lang == "en" else f"La relation statistique la plus forte apparait entre {x_name} et {y_name}."
    else:
        insight = "Several numeric variables move together, but no single relationship dominates." if lang == "en" else "Plusieurs variables numeriques evoluent ensemble, sans qu'une relation unique domine."
    if strongest_positive:
        pos_x, pos_y = strongest_positive
        fig.add_annotation(
            x=pos_x,
            y=pos_y,
            text="Opportunity cluster" if lang == "en" else "Zone d'opportunite",
            showarrow=False,
            font={"color": OPPORTUNITY_GREEN, "size": 11},
            bgcolor="rgba(255,252,247,0.95)",
            bordercolor=OPPORTUNITY_GREEN,
            yshift=-18,
        )
    if strongest_negative:
        neg_x, neg_y = strongest_negative
        neg_text = ("Price increase -> demand drop" if {str(neg_x).lower(), str(neg_y).lower()} & {"price", "units_sold"} == {"price", "units_sold"} else "Risk trade-off") if lang == "en" else ("Hausse de prix -> baisse de la demande" if {str(neg_x).lower(), str(neg_y).lower()} & {"price", "units_sold"} == {"price", "units_sold"} else "Arbitrage de risque")
        fig.add_annotation(
            x=neg_x,
            y=neg_y,
            text=neg_text,
            showarrow=False,
            font={"color": RISK_RED, "size": 11},
            bgcolor="rgba(255,252,247,0.95)",
            bordercolor=RISK_RED,
            yshift=18,
        )
    why = "This chart quickly surfaces which variables may deserve deeper business investigation, feature engineering, or simulation." if lang == "en" else "Ce graphique montre rapidement quelles variables meritent une investigation business plus approfondie, du feature engineering ou une simulation."
    return _chart_card(
        title="Correlation Heatmap" if lang == "en" else "Heatmap de correlation",
        insight=insight,
        why_it_matters=why,
        impact_level="medium",
        confidence="medium",
        fig=fig,
        question="Which variables move together strongly enough to matter for decisions?" if lang == "en" else "Quelles variables evoluent assez fortement ensemble pour compter dans la decision ?",
    )


def _build_price_demand_chart(df: pd.DataFrame, lang: str = "en") -> Optional[dict[str, Any]]:
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
                name="Observed records" if lang == "en" else "Observations",
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
                name="High-price weak-response points" if lang == "en" else "Points prix eleves / faible reponse",
            )
        )
        sample = highlighted.iloc[0]
        fig.add_annotation(
            x=float(sample["price"]),
            y=float(sample[y_col]),
            text=("Price increase coincides with lower volume" if y_col == "units_sold" else "High-price weak revenue point") if lang == "en" else ("La hausse de prix coincide avec un volume plus faible" if y_col == "units_sold" else "Point prix eleve / revenu faible"),
            showarrow=True,
            arrowcolor=RISK_RED,
            bgcolor="rgba(255,252,247,0.95)",
            font={"color": RISK_RED},
        )

    fig = _apply_premium_layout(
        fig,
        f"Price vs {y_col.replace('_', ' ').title()}" if lang == "en" else f"Prix vs {y_col.replace('_', ' ').title()}",
        "Outliers and potentially risky price-response observations are highlighted." if lang == "en" else "Les observations atypiques et les points de reponse prix potentiellement risquee sont mis en avant.",
    )
    corr = float(clean[["price", y_col]].corr().iloc[0, 1])
    insight = f"The measured relationship between price and {y_col} is {corr:.2f}, with unusual observations flagged where price is high and response is weak." if lang == "en" else f"La relation mesuree entre prix et {y_col} est de {corr:.2f}, avec des observations inhabituelles la ou le prix est eleve et la reponse faible."
    why = "This view is designed for pricing conversations, not just exploration. It helps quickly spot elasticity risk and unusual exceptions." if lang == "en" else "Cette vue est concue pour les discussions de pricing, pas seulement pour l'exploration. Elle aide a reperer vite le risque d'elasticite et les exceptions."
    impact = "high" if abs(corr) >= 0.5 else "medium"
    return _chart_card(
        title="Price Sensitivity View" if lang == "en" else "Vue de sensibilite prix",
        insight=insight,
        why_it_matters=why,
        impact_level=impact,
        confidence="medium",
        fig=fig,
        question=f"Does price appear to change {y_col.replace('_', ' ')} in a meaningful way?" if lang == "en" else f"Le prix semble-t-il faire varier {y_col.replace('_', ' ')} de facon significative ?",
    )


def _build_segment_comparison_chart(df: pd.DataFrame, lang: str = "en") -> Optional[dict[str, Any]]:
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
        f"{metric.capitalize()} by {segment_col.capitalize()}" if lang == "en" else f"{metric.capitalize()} par {segment_col.capitalize()}",
        "Best and worst performers are emphasized to support prioritization." if lang == "en" else "Les meilleurs et moins bons performeurs sont mis en avant pour faciliter la priorisation.",
    )
    best = grouped.iloc[0]
    worst = grouped.iloc[-1]
    fig.add_annotation(
        x=float(best[metric]),
        y=str(best[segment_col]),
        text="Best performer" if lang == "en" else "Meilleur performeur",
        showarrow=True,
        arrowcolor=OPPORTUNITY_GREEN,
        font={"color": OPPORTUNITY_GREEN},
        bgcolor="rgba(255,252,247,0.95)",
    )
    fig.add_annotation(
        x=float(worst[metric]),
        y=str(worst[segment_col]),
        text=(f"{worst[segment_col]} underperforms" if lang == "en" else f"{worst[segment_col]} sous-performe"),
        showarrow=True,
        arrowcolor=RISK_RED,
        font={"color": RISK_RED},
        bgcolor="rgba(255,252,247,0.95)",
    )
    overall_mean = float(grouped[metric].mean())
    fig.add_vline(x=overall_mean, line_dash="dash", line_color=BASELINE_BLUE, opacity=0.35)
    fig.add_annotation(
        x=overall_mean,
        y=1.02,
        yref="paper",
        text="Portfolio average" if lang == "en" else "Moyenne portefeuille",
        showarrow=False,
        font={"color": BASELINE_BLUE},
        bgcolor="rgba(255,252,247,0.95)",
    )
    gap = float(best[metric] - worst[metric])
    insight = f"{best[segment_col]} leads while {worst[segment_col]} trails, creating an average {metric} gap of {gap:.2f}." if lang == "en" else f"{best[segment_col]} est en tete tandis que {worst[segment_col]} est en retrait, avec un ecart moyen de {metric} de {gap:.2f}."
    why = "Segment comparison turns broad performance noise into a prioritization conversation about where to protect, fix, or invest." if lang == "en" else "La comparaison par segment transforme un bruit de performance global en discussion de priorisation sur ce qu'il faut proteger, corriger ou financer."
    return _chart_card(
        title="Segment Comparison" if lang == "en" else "Comparaison de segments",
        insight=insight,
        why_it_matters=why,
        impact_level="high",
        confidence="high",
        fig=fig,
        question="Which regions, products, or channels are outperforming or underperforming?" if lang == "en" else "Quelles regions, quels produits ou quels canaux surperforment ou sous-performent ?",
    )


def build_chart_specs(df: pd.DataFrame, lang: str = "en") -> list[dict]:
    cards: list[dict] = []
    for builder in [
        _build_trend_anomaly_chart,
        _build_correlation_heatmap,
        _build_price_demand_chart,
        _build_segment_comparison_chart,
    ]:
        chart_card = builder(df, lang)
        if chart_card:
            cards.append(chart_card)
    return cards[:5]


def build_feature_importance_chart(feature_importance: list[dict]) -> dict:
    if not feature_importance:
        fig = _apply_premium_layout(go.Figure(), "No Feature Importance Available")
        return _json_safe_figure(fig)

    top_items = list(reversed(feature_importance[:7]))
    top_values = [float(item["importance"]) for item in feature_importance[:3]]
    top_share = (sum(top_values) / sum(float(item["importance"]) for item in feature_importance)) * 100 if feature_importance else 0.0
    fig = go.Figure(
        data=[
            go.Bar(
                x=[float(item["importance"]) for item in top_items],
                y=[_clean_feature_name(str(item["feature"])) for item in top_items],
                orientation="h",
                marker_color=[OPPORTUNITY_GREEN if idx == len(top_items) - 1 else BASELINE_BLUE for idx, _ in enumerate(top_items)],
                text=[round(float(item["importance"]), 3) for item in top_items],
                textposition="outside",
            )
        ]
    )
    top_driver = _clean_feature_name(str(feature_importance[0]["feature"]))
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
    fig.add_annotation(
        x=float(top_items[0]["importance"]),
        y=_clean_feature_name(str(top_items[0]["feature"])),
        text=f"Top 3 explain {top_share:.0f}% of model signal",
        showarrow=False,
        xanchor="left",
        xshift=12,
        font={"color": BASELINE_BLUE},
        bgcolor="rgba(255,252,247,0.95)",
    )
    return _json_safe_figure(fig)


def build_scenario_comparison_chart(labels: list[str], values: list[float], delta_pcts: Optional[list[Optional[float]]] = None) -> dict:
    colors = [BASELINE_BLUE]
    for idx in range(1, len(labels)):
        pct = delta_pcts[idx] if delta_pcts and idx < len(delta_pcts) else None
        colors.append(OPPORTUNITY_GREEN if pct is not None and pct >= 0 else RISK_RED)
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
                fig.add_annotation(
                    x=labels[idx],
                    y=values[idx] / 2 if values[idx] else 0,
                    text="Opportunity scenario" if pct >= 0 else "Risk scenario",
                    showarrow=False,
                    font={"color": OPPORTUNITY_GREEN if pct >= 0 else RISK_RED, "size": 11},
                )
    if len(values) >= 2:
        baseline = values[0]
        first_scenario = values[1]
        fig.add_annotation(
            x=labels[1],
            y=max(baseline, first_scenario),
            text=f"Baseline vs scenario: {_format_value(first_scenario - baseline)} delta",
            showarrow=True,
            arrowcolor=BASELINE_BLUE,
            bgcolor="rgba(255,252,247,0.95)",
            font={"color": BASELINE_BLUE},
            ay=-40,
        )
    return _json_safe_figure(fig)


def build_localized_scenario_comparison_chart(
    labels: list[str],
    values: list[float],
    delta_pcts: Optional[list[Optional[float]]] = None,
    *,
    title: str,
    subtitle: str,
    winner_label: Optional[str] = None,
) -> dict:
    colors = [BASELINE_BLUE]
    for idx in range(1, len(labels)):
        pct = delta_pcts[idx] if delta_pcts and idx < len(delta_pcts) else None
        colors.append(OPPORTUNITY_GREEN if pct is not None and pct >= 0 else RISK_RED)
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
    fig = _apply_premium_layout(fig, title, subtitle)
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
    if winner_label and len(labels) > 1:
        fig.add_annotation(
            x=labels[-1],
            y=max(values),
            text=winner_label,
            showarrow=True,
            arrowcolor=OPPORTUNITY_GREEN,
            bgcolor="rgba(255,252,247,0.95)",
            font={"color": OPPORTUNITY_GREEN},
            ay=-40,
        )
    return _json_safe_figure(fig)


def build_decision_impact_chart(impact_views: list[dict[str, Any]], *, title: str, subtitle: str, annotation: str) -> dict:
    labels = [item["label"] for item in impact_views]
    delta_pcts = [float(item["delta_pct"] or 0.0) for item in impact_views]
    fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=delta_pcts,
                marker_color=[OPPORTUNITY_GREEN if value >= 0 else RISK_RED for value in delta_pcts],
                text=[f"{value:+.1f}%" for value in delta_pcts],
                textposition="outside",
            )
        ]
    )
    fig = _apply_premium_layout(fig, title, subtitle)
    fig.update_yaxes(title="Delta %")
    if labels:
        max_idx = int(np.argmax(np.abs(delta_pcts)))
        fig.add_annotation(
            x=labels[max_idx],
            y=delta_pcts[max_idx],
            text=annotation,
            showarrow=True,
            arrowcolor=BASELINE_BLUE,
            bgcolor="rgba(255,252,247,0.95)",
            font={"color": BASELINE_BLUE},
            ay=-35,
        )
    return _json_safe_figure(fig)


def build_decision_risk_chart(items: list[dict[str, Any]], *, title: str, subtitle: str, annotation: str) -> dict:
    fig = go.Figure(
        data=[
            go.Bar(
                x=[item["label"] for item in items],
                y=[float(item["score"]) for item in items],
                marker_color=[RISK_RED if float(item["score"]) >= 70 else WARN_ORANGE if float(item["score"]) >= 40 else BASELINE_BLUE for item in items],
                text=[str(item["text"]) for item in items],
                textposition="outside",
            )
        ]
    )
    fig = _apply_premium_layout(fig, title, subtitle)
    fig.update_yaxes(title="Risk score")
    if items:
        top = max(items, key=lambda item: float(item["score"]))
        fig.add_annotation(
            x=top["label"],
            y=float(top["score"]),
            text=annotation,
            showarrow=True,
            arrowcolor=RISK_RED,
            bgcolor="rgba(255,252,247,0.95)",
            font={"color": RISK_RED},
            ay=-35,
        )
    return _json_safe_figure(fig)


def build_root_cause_driver_chart(drivers: list[dict[str, str]], metric: str) -> dict:
    if not drivers:
        return _json_safe_figure(_apply_premium_layout(go.Figure(), f"Root-Cause Drivers for {metric}"))

    ranked = sorted(drivers, key=lambda driver: _parse_magnitude(driver.get("impact_estimate")), reverse=True)
    ordered = list(reversed(ranked))
    y_labels = [driver["driver"] for driver in ordered]
    scores = [_parse_magnitude(driver["impact_estimate"]) for driver in ordered]
    colors = [RISK_RED if "trend" in label.lower() else WARN_ORANGE if "segment" in label.lower() else BASELINE_BLUE for label in y_labels]
    fig = go.Figure(
        data=[
            go.Bar(
                x=scores,
                y=y_labels,
                orientation="h",
                marker_color=colors,
                text=[driver["impact_estimate"] for driver in ordered],
                textposition="outside",
            )
        ]
    )
    fig = _apply_premium_layout(
        fig,
        f"Root-Cause Driver View For {metric}",
        "Top drivers are ranked by contribution strength to focus validation effort.",
    )
    fig.add_annotation(
        x=scores[-1],
        y=y_labels[-1],
        text="Top driver",
        showarrow=True,
        arrowcolor=RISK_RED,
        font={"color": RISK_RED},
        bgcolor="rgba(255,252,247,0.95)",
    )
    return _json_safe_figure(fig)
