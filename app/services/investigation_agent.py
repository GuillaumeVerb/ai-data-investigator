from __future__ import annotations

from typing import Any, Dict, List
from uuid import uuid4

import pandas as pd
import plotly.graph_objects as go

from app.core.schemas import InvestigationPathResponse, InvestigationSuggestion
from app.core.state import store
from app.services.charts import _json_safe_figure


def build_investigation_suggestions(df: pd.DataFrame, language: str = "en") -> List[InvestigationSuggestion]:
    suggestions: List[InvestigationSuggestion] = []
    lang = "fr" if language == "fr" else "en"
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    datetime_columns = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns.tolist()

    if datetime_columns and "revenue" in df.columns:
        suggestions.append(
            InvestigationSuggestion(
                suggestion_id=str(uuid4()),
                title="Revenue trend changed over time" if lang == "en" else "La tendance du revenu a evolue dans le temps",
                explanation=(
                    "The dataset contains time structure and revenue, making post-period shifts worth reviewing."
                    if lang == "en"
                    else "Le dataset contient une structure temporelle et du revenu, ce qui rend les changements de periode utiles a examiner."
                ),
                expected_impact=(
                    "Clarifies whether performance pressure is recent, persistent, or seasonal before action is taken."
                    if lang == "en"
                    else "Clarifie si la pression sur la performance est recente, persistante ou saisonniere avant d'agir."
                ),
                investigation_type="trend",
                priority_score=0.91,
                confidence_pct=91,
                payload={"value_column": "revenue", "date_column": datetime_columns[0]},
            )
        )

    if {"price", "units_sold"}.issubset(df.columns):
        suggestions.append(
            InvestigationSuggestion(
                suggestion_id=str(uuid4()),
                title="Strong relationship between price and units_sold" if lang == "en" else "Relation forte entre prix et units_sold",
                explanation=(
                    "Price changes may be materially linked to sales volume and should be explored more deeply."
                    if lang == "en"
                    else "Les changements de prix peuvent etre fortement lies au volume de ventes et meriter une analyse plus approfondie."
                ),
                expected_impact=(
                    "Improves pricing decisions by identifying likely volume sensitivity and margin trade-offs."
                    if lang == "en"
                    else "Ameliore les decisions pricing en identifiant la sensibilite probable du volume et les arbitrages de marge."
                ),
                investigation_type="correlation",
                priority_score=0.88,
                confidence_pct=88,
                payload={"left": "price", "right": "units_sold"},
            )
        )

    if "region" in df.columns and numeric_columns:
        suggestions.append(
            InvestigationSuggestion(
                suggestion_id=str(uuid4()),
                title="Some regions behave differently from the rest of the dataset" if lang == "en" else "Certaines regions se comportent differemment du reste du dataset",
                explanation=(
                    "Regional divergence may reflect meaningful commercial opportunities or operational risks."
                    if lang == "en"
                    else "Les ecarts regionaux peuvent refleter des opportunites commerciales importantes ou des risques operationnels."
                ),
                expected_impact=(
                    "Helps prioritize where commercial intervention or operational review could matter most."
                    if lang == "en"
                    else "Aide a prioriser les zones ou une action commerciale ou une revue operationnelle peut avoir le plus d'effet."
                ),
                investigation_type="segment",
                priority_score=0.82,
                confidence_pct=82,
                payload={"segment_column": "region", "value_column": numeric_columns[0]},
            )
        )

    if numeric_columns:
        suggestions.append(
            InvestigationSuggestion(
                suggestion_id=str(uuid4()),
                title="Outlier records may be driving a share of the performance story" if lang == "en" else "Des observations extremes peuvent expliquer une partie importante de la performance",
                explanation=(
                    "A small number of extreme rows may explain a disproportionate amount of movement."
                    if lang == "en"
                    else "Un petit nombre de lignes extremes peut expliquer une part disproportionnee des variations."
                ),
                expected_impact=(
                    "Reduces the risk of acting on noisy or exceptional observations as if they were broad trends."
                    if lang == "en"
                    else "Reduit le risque d'agir sur des observations bruitees ou exceptionnelles comme si elles representaient une tendance large."
                ),
                investigation_type="anomaly",
                priority_score=0.74,
                confidence_pct=74,
                payload={"numeric_columns": numeric_columns[:5]},
            )
        )

    if categorical_columns and "revenue" in df.columns:
        suggestions.append(
            InvestigationSuggestion(
                suggestion_id=str(uuid4()),
                title="Channel or segment mix may explain revenue concentration" if lang == "en" else "Le mix canal ou segment peut expliquer la concentration du revenu",
                explanation=(
                    "Comparing revenue by segment can reveal where performance is concentrated or diluted."
                    if lang == "en"
                    else "Comparer le revenu par segment peut montrer ou la performance se concentre ou se dilue."
                ),
                expected_impact=(
                    "Supports sharper prioritization by showing which segments deserve more focus or protection."
                    if lang == "en"
                    else "Aide a une priorisation plus nette en montrant quels segments meritent plus d'attention ou de protection."
                ),
                investigation_type="segment",
                priority_score=0.71,
                confidence_pct=71,
                payload={"segment_column": categorical_columns[0], "value_column": "revenue"},
            )
        )

    return sorted(suggestions, key=lambda item: item.priority_score, reverse=True)[:5]


def investigate_path(dataset_id: str, suggestion_id: str, payload: Dict[str, Any], language: str = "en") -> InvestigationPathResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe
    inv_type = payload.get("investigation_type")
    lang = "fr" if language == "fr" else "en"

    if inv_type == "trend" or {"value_column", "date_column"}.issubset(payload):
        value_col = payload["value_column"]
        date_col = payload["date_column"]
        ordered = df.sort_values(date_col).copy()
        ordered["period"] = ordered[date_col].dt.to_period("M").astype(str)
        grouped = ordered.groupby("period", dropna=False)[value_col].mean().reset_index()
        change = grouped[value_col].iloc[-1] - grouped[value_col].iloc[0] if len(grouped) >= 2 else 0
        fig = go.Figure(data=[go.Scatter(x=grouped["period"], y=grouped[value_col], mode="lines+markers")])
        fig.update_layout(title=f"{value_col} over time" if lang == "en" else f"{value_col} dans le temps", xaxis_title="period" if lang == "en" else "periode", yaxis_title=value_col)
        return InvestigationPathResponse(
            suggestion_id=suggestion_id,
            title="Focused trend investigation" if lang == "en" else "Investigation ciblee de tendance",
            analysis=(
                f"{value_col} changes by {change:.2f} between the earliest and latest observed periods."
                if lang == "en"
                else f"{value_col} varie de {change:.2f} entre les periodes la plus ancienne et la plus recente observees."
            ),
            business_implication=(
                "Performance appears to shift over time, so decisions should compare recent versus historical behavior."
                if lang == "en"
                else "La performance semble evoluer dans le temps, donc les decisions doivent comparer le recent a l'historique."
            ),
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
            title="Focused correlation investigation" if lang == "en" else "Investigation ciblee de correlation",
            analysis=(
                f"The measured correlation between {left} and {right} is {correlation:.2f}."
                if lang == "en"
                else f"La correlation mesuree entre {left} et {right} est de {correlation:.2f}."
            ),
            business_implication=(
                "This relationship may indicate a pricing-response dynamic worth testing in a controlled way."
                if lang == "en"
                else "Cette relation peut indiquer une dynamique de reponse au prix qui merite un test controle."
            ),
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
        fig.update_layout(title=f"{value_col} by {segment_col}" if lang == "en" else f"{value_col} par {segment_col}", xaxis_title=segment_col, yaxis_title=value_col)
        return InvestigationPathResponse(
            suggestion_id=suggestion_id,
            title="Focused segment investigation" if lang == "en" else "Investigation ciblee de segment",
            analysis=(
                f"The top segment outperforms the bottom segment by {gap:.2f} on average {value_col}."
                if lang == "en"
                else f"Le meilleur segment surperforme le moins bon de {gap:.2f} en moyenne sur {value_col}."
            ),
            business_implication=(
                "Segment performance is uneven, so broad strategies may be leaving value on the table."
                if lang == "en"
                else "La performance des segments est inegale, donc une strategie trop large peut laisser de la valeur de cote."
            ),
            supporting_stats={"segments": int(len(grouped)), "gap": round(float(gap), 2)},
            chart_spec=_json_safe_figure(fig),
        )

    numeric_columns = payload.get("numeric_columns", [])
    subset = df[numeric_columns].copy() if numeric_columns else df.select_dtypes(include=["number"]).copy()
    z_scores = (subset - subset.mean()) / subset.std(ddof=0).replace(0, 1)
    anomaly_count = int((z_scores.abs().max(axis=1) > 2.2).sum())
    return InvestigationPathResponse(
        suggestion_id=suggestion_id,
        title="Focused anomaly investigation" if lang == "en" else "Investigation ciblee d'anomalie",
        analysis=(
            f"{anomaly_count} rows show unusually large deviations across the monitored numeric variables."
            if lang == "en"
            else f"{anomaly_count} lignes montrent des deviations inhabituellement fortes sur les variables numeriques suivies."
        ),
        business_implication=(
            "Extreme observations may represent errors, special events, or operational edge cases."
            if lang == "en"
            else "Des observations extremes peuvent representer des erreurs, des evenements speciaux ou des cas limites operationnels."
        ),
        supporting_stats={"anomaly_count": anomaly_count},
        chart_spec=None,
    )
