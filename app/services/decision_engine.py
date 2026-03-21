from __future__ import annotations

import math
from typing import Any, Dict, Optional, Union

import pandas as pd

from app.core.schemas import (
    DecisionComparison,
    DecisionConfidence,
    DecisionEngineResponse,
    DecisionEvidencePack,
    DecisionImpactView,
    DecisionInputControl,
    DecisionScenarioComparison,
    DecisionScenarioRow,
    MissingDataRecommendation,
)
from app.core.state import store
from app.services.action_engine import recommend_actions
from app.services.charts import (
    build_decision_impact_chart,
    build_decision_risk_chart,
    build_feature_importance_chart,
    build_localized_scenario_comparison_chart,
)
from app.services.enrichment_agent import suggest_enrichment
from app.services.scenario_engine import (
    _apply_changes,
    _compute_delta,
    build_feature_frame,
    build_reference_row,
    normalize_scenario_changes,
    predict_row,
    row_coverage_pct,
)
from app.ui.i18n import t

DISCLAIMER = {
    "en": "This recommendation is based on model behavior and observed data patterns, not causal inference.",
    "fr": "Cette recommandation repose sur le comportement du modele et les tendances observees, pas sur une causalite prouvee.",
}
MATERIALITY_THRESHOLD_PCT = 2.0


def _serialize_row(row: pd.Series) -> Dict[str, Any]:
    return row.astype(object).where(pd.notnull(row), None).to_dict()


def _find_segment_candidates(feature_columns: list[str], df: pd.DataFrame) -> list[str]:
    preferred = ["region", "customer_segment"]
    categorical = [column for column in feature_columns if column in df.columns and df[column].dtype == object]
    ordered = [column for column in preferred if column in categorical]
    ordered.extend([column for column in categorical if column not in ordered and column not in {"product", "channel"}])
    return ordered


def _find_product_control(feature_columns: list[str], df: pd.DataFrame, lang: str) -> Optional[DecisionInputControl]:
    if "product" in feature_columns:
        options = sorted(df["product"].dropna().astype(str).unique().tolist())
        return DecisionInputControl(
            key="product_mix",
            label="Product Mix" if lang == "en" else "Mix produit",
            control_type="selectbox",
            default_value=options[0] if options else None,
            options=options,
        )

    product_share_columns = [column for column in feature_columns if "product_mix" in column or "share" in column]
    if product_share_columns:
        return DecisionInputControl(
            key=product_share_columns[0],
            label=product_share_columns[0].replace("_", " ").title(),
            control_type="slider",
            default_value=0.0,
            min_value=0.0,
            max_value=100.0,
        )

    return DecisionInputControl(
        key="product_mix",
        label="Product Mix" if lang == "en" else "Mix produit",
        control_type="selectbox",
        available=False,
        reason="No product or product-share fields are available in the trained feature set."
        if lang == "en"
        else "Aucun champ produit ou part de produit n'est disponible dans les variables du modele.",
        options=[],
    )


def _build_available_inputs(base_row: pd.Series, feature_columns: list[str], df: pd.DataFrame, lang: str) -> list[DecisionInputControl]:
    controls: list[DecisionInputControl] = []
    numeric_fields = {
        "price": "Price" if lang == "en" else "Prix",
        "marketing_spend": "Marketing Spend" if lang == "en" else "Depenses marketing",
    }
    discount_key = "discount_pct" if "discount_pct" in feature_columns else "discount" if "discount" in feature_columns else None
    if discount_key:
        numeric_fields[discount_key] = "Discount" if lang == "en" else "Remise"

    for key, label in numeric_fields.items():
        if key in base_row.index and base_row[key] is not None:
            value = float(base_row[key])
            controls.append(
                DecisionInputControl(
                    key="discount" if key in {"discount", "discount_pct"} else key,
                    label=label,
                    control_type="slider",
                    min_value=round(value * 0.5, 2),
                    max_value=round(min(value * 1.5 + 1, value + max(abs(value * 0.1), 5)), 2),
                    default_value=value,
                )
            )

    if "region" in feature_columns:
        controls.append(
            DecisionInputControl(
                key="region",
                label="Region" if lang == "en" else "Region",
                control_type="selectbox",
                default_value=str(base_row.get("region")) if base_row.get("region") is not None else None,
                options=sorted(df["region"].dropna().astype(str).unique().tolist()),
            )
        )

    controls.append(_find_product_control(feature_columns, df, lang))
    return controls


def _data_size_band(size: int, lang: str) -> str:
    if size >= 500:
        return "large" if lang == "en" else "grand"
    if size >= 100:
        return "medium" if lang == "en" else "moyen"
    return "small" if lang == "en" else "limite"


def _model_reliability_label(primary_metric_name: str, primary_metric_value: float, lang: str) -> str:
    level = "low"
    if primary_metric_name == "r2":
        level = "high" if primary_metric_value >= 0.75 else "medium" if primary_metric_value >= 0.5 else "low"
    else:
        level = "high" if primary_metric_value >= 0.8 else "medium" if primary_metric_value >= 0.6 else "low"
    if lang == "fr":
        return {"high": "elevee", "medium": "moyenne", "low": "faible"}[level]
    return level


def _normalized_level(label: str) -> str:
    return {"elevee": "high", "moyenne": "medium", "faible": "low"}.get(label, label)


def _combined_confidence(model_reliability: str, row_coverage: float, data_size: str) -> str:
    normalized = _normalized_level(model_reliability)
    normalized_size = {"grand": "large", "moyen": "medium", "limite": "small"}.get(data_size, data_size)
    score = {"low": 0, "medium": 1, "high": 2}[normalized]
    score += 2 if row_coverage >= 95 else 1 if row_coverage >= 80 else 0
    score += {"small": 0, "medium": 1, "large": 2}[normalized_size]
    if score >= 5:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


def _prediction_score(model_id: str, row: pd.Series) -> float:
    model_record = store.get_model(model_id)
    frame = pd.DataFrame([row])
    pipeline = model_record.pipeline
    if model_record.task_type == "classification" and hasattr(pipeline, "predict_proba"):
        probabilities = pipeline.predict_proba(frame)[0]
        return float(max(probabilities))
    prediction = predict_row(model_id, row)
    if isinstance(prediction, float):
        return prediction
    return 0.0


def _confidence_label(level: str, lang: str) -> str:
    if lang == "fr":
        return {"high": "Elevee", "medium": "Moyenne", "low": "Faible"}[level]
    return level.title()


def _robustness_label(level: str, lang: str) -> str:
    if lang == "fr":
        return {"high": "Elevee", "medium": "Moyenne", "low": "Faible"}[level]
    return level.title()


def _decision_label(decision: str, lang: str) -> str:
    mapping = {
        "baseline": {"en": "keep the baseline plan", "fr": "conserver le plan de reference"},
        "scenario_a": {"en": "execute Scenario A", "fr": "executer le Scenario A"},
        "scenario_b": {"en": "execute Scenario B", "fr": "executer le Scenario B"},
    }
    return mapping[decision][lang]


def _scenario_risk(changes: Dict[str, Any], row_coverage: float, model_reliability: str, lang: str) -> str:
    normalized = _normalized_level(model_reliability)
    if normalized == "low":
        return (
            "Model reliability is low, so scenario ranking may not hold outside the current sample."
            if lang == "en"
            else "La fiabilite du modele est faible, donc le classement des scenarios peut ne pas tenir hors de l'echantillon actuel."
        )
    if row_coverage < 85:
        return (
            "The simulated row has limited coverage, which weakens confidence in the recommendation."
            if lang == "en"
            else "La ligne simulee a une couverture limitee, ce qui reduit la confiance dans la recommandation."
        )
    if "price" in changes and "discount_pct" in changes:
        return (
            "Price and discount moved together, which can hide true elasticity and margin trade-offs."
            if lang == "en"
            else "Le prix et la remise ont evolue ensemble, ce qui peut masquer la veritable elasticite et les arbitrages de marge."
        )
    if "price" in changes:
        return (
            "The main risk is a demand drop if price sensitivity is stronger than the model indicates."
            if lang == "en"
            else "Le risque principal est une baisse de la demande si la sensibilite prix est plus forte que ce qu'indique le modele."
        )
    if "marketing_spend" in changes:
        return (
            "The main risk is lower efficiency if additional spend saturates response."
            if lang == "en"
            else "Le risque principal est une efficacite plus faible si les depenses additionnelles saturent la reponse."
        )
    if "region" in changes or "product" in changes:
        return (
            "The main risk is over-generalizing a segment or mix effect to the full business."
            if lang == "en"
            else "Le risque principal est de generaliser a toute l'activite un effet propre a un segment ou a un mix."
        )
    return (
        "The recommendation is directional and should be validated with a controlled business test."
        if lang == "en"
        else "La recommandation est directionnelle et doit etre validee par un test business controle."
    )


def _guardrails(
    winning_changes: Dict[str, Any],
    *,
    confidence_level: str,
    segment_divergence: bool,
    lang: str,
) -> list[str]:
    items: list[str] = []
    if "price" in winning_changes:
        items.append(
            "Keep the price move at or below 10% and monitor weekly."
            if lang == "en"
            else "Limiter la variation de prix a 10 % maximum et suivre les resultats chaque semaine."
        )
    if segment_divergence:
        items.append(
            "Do not roll out globally; start with the most resilient segment first."
            if lang == "en"
            else "Ne pas deployer globalement ; commencer par le segment le plus resilient."
        )
    if confidence_level == "low":
        items.append(
            "Treat the recommendation as directional only until more data or tests are available."
            if lang == "en"
            else "Traiter la recommandation comme directionnelle tant que davantage de donnees ou de tests ne sont pas disponibles."
        )
    items.append(
        "Do not over-interpret weak model signals."
        if lang == "en"
        else "Ne pas sur-interpreter des signaux de modele faibles."
    )
    return items


def _next_best_analysis(changes: Dict[str, Any], lang: str) -> str:
    if "price" in changes:
        return (
            "Run a price-sensitivity and segment elasticity review before rollout."
            if lang == "en"
            else "Mener une analyse de sensibilite prix et d'elasticite par segment avant de deployer."
        )
    if "marketing_spend" in changes:
        return (
            "Compare marginal response by channel or region to confirm spend efficiency."
            if lang == "en"
            else "Comparer la reponse marginale par canal ou region pour confirmer l'efficacite des depenses."
        )
    if "region" in changes:
        return (
            "Review segment comparison and root-cause evidence for the selected region."
            if lang == "en"
            else "Examiner la comparaison par segment et les elements de cause racine pour la region selectionnee."
        )
    if "product" in changes or "product_mix" in changes:
        return (
            "Inspect product-level margin and demand trade-offs before changing the mix."
            if lang == "en"
            else "Examiner les arbitrages marge-demande au niveau produit avant de changer le mix."
        )
    return (
        "Review top model drivers and segment variance before acting on the scenario."
        if lang == "en"
        else "Examiner les principaux leviers du modele et la variance par segment avant d'agir."
    )


def _decision_summary(
    *,
    baseline_prediction: Union[float, str],
    scenario_a_prediction: Union[float, str],
    scenario_b_prediction: Optional[Union[float, str]],
    baseline_score: float,
    scenario_a_score: float,
    scenario_b_score: Optional[float],
    confidence_level: str,
    task_type: str,
) -> tuple[str, Union[float, str], Union[float, str], Union[float, str], Optional[float]]:
    winner = "scenario_a"
    winner_prediction = scenario_a_prediction
    winner_score = scenario_a_score
    if scenario_b_prediction is not None and scenario_b_score is not None and scenario_b_score > scenario_a_score:
        winner = "scenario_b"
        winner_prediction = scenario_b_prediction
        winner_score = scenario_b_score

    delta, delta_pct, _ = _compute_delta(baseline_prediction, winner_prediction)
    material = isinstance(delta_pct, float) and abs(delta_pct) >= MATERIALITY_THRESHOLD_PCT
    if task_type == "classification":
        material = not math.isclose(winner_score, baseline_score, rel_tol=0.0, abs_tol=0.02)

    if confidence_level == "low" or not material:
        return "baseline", baseline_prediction, baseline_prediction, 0.0 if isinstance(baseline_prediction, float) else f"{baseline_prediction} -> {baseline_prediction}", 0.0 if isinstance(baseline_prediction, float) else None

    return winner, baseline_prediction, winner_prediction, delta, delta_pct


def _impact_view(
    *,
    view_key: str,
    label: str,
    baseline_prediction: Union[float, str],
    recommended_prediction: Union[float, str],
    lang: str,
) -> DecisionImpactView:
    delta, delta_pct, _ = _compute_delta(baseline_prediction, recommended_prediction)
    insight = ""
    if view_key == "reference_row":
        insight = t("decision_engine.insight.stronger_local", lang)
    elif view_key == "dataset_average":
        insight = (
            "The global average gives a calmer view of the expected impact."
            if lang == "en"
            else "La moyenne globale donne une lecture plus stable de l'impact attendu."
        )
    else:
        insight = (
            "The selected segment helps validate whether the recommendation should stay targeted."
            if lang == "en"
            else "Le segment selectionne aide a verifier si la recommandation doit rester ciblee."
        )
    return DecisionImpactView(
        view_key=view_key,  # type: ignore[arg-type]
        label=label,
        baseline_prediction=baseline_prediction,
        recommended_prediction=recommended_prediction,
        delta=delta,
        delta_pct=delta_pct,
        insight=insight,
    )


def _build_segment_row(df: pd.DataFrame, feature_columns: list[str], segment_column: str, segment_value: str) -> Optional[pd.Series]:
    filtered = df[df[segment_column].astype(str) == str(segment_value)]
    if filtered.empty:
        return None
    return build_reference_row(filtered, feature_columns, baseline_mode="dataset_average", reference_index=None)


def _extract_join_key(integration_hint: str) -> str:
    lower = integration_hint.lower()
    for key in ["customer_id", "customer", "account", "date", "region", "product", "channel"]:
        if key in lower:
            return key
    return "date"


def _missing_data_recommendations(dataset_id: str, lang: str) -> list[MissingDataRecommendation]:
    enrichment = suggest_enrichment(dataset_id)
    results: list[MissingDataRecommendation] = []
    for item in enrichment.suggestions:
        why = item.why_it_matters
        expected = item.expected_value
        merge_hint = _extract_join_key(item.integration_hint)
        if lang == "fr":
            why = {
                "Campaign timing can explain spikes or drops that are invisible in transactional data alone.": "Le calendrier des campagnes peut expliquer des pics ou des baisses invisibles dans les seules donnees transactionnelles.",
                "Holidays, promotions, and seasonality often distort trends and should be separated from core demand.": "Les jours feries, promotions et effets de saisonnalite perturbent souvent les tendances et doivent etre separes de la demande de fond.",
                "Without segment attributes, it is hard to know which audiences drive or drag performance.": "Sans attributs de segment, il est difficile de savoir quels publics soutiennent ou freinent la performance.",
                "Regional underperformance may come from stock availability rather than demand weakness.": "Une sous-performance regionale peut venir de contraintes de stock plutot que d'une faiblesse de la demande.",
            }.get(why, why)
            expected = {
                "Better attribution of demand changes and stronger scenario recommendations.": "Une meilleure attribution des variations de demande et des recommandations de scenarios plus solides.",
                "Cleaner trend interpretation and more credible root-cause explanations.": "Une interpretation plus propre des tendances et des explications plus credibles des causes racines.",
                "Sharper targeting, better recommendations, and clearer driver analysis.": "Un ciblage plus precis, de meilleures recommandations et une analyse des leviers plus claire.",
                "More accurate diagnosis of whether issues are commercial or operational.": "Un diagnostic plus precis pour distinguer problemes commerciaux et operationnels.",
            }.get(expected, expected)
        results.append(
            MissingDataRecommendation(
                dataset_name=item.dataset_name if lang == "en" else {
                    "Marketing campaigns": "Campagnes marketing",
                    "External calendar factors": "Facteurs calendaires externes",
                    "Customer segmentation data": "Donnees de segmentation client",
                    "Inventory or supply constraints": "Contraintes de stock ou de supply",
                }.get(item.dataset_name, item.dataset_name),
                why_it_matters=why,
                what_it_improves=expected,
                merge_hint=merge_hint,
            )
        )
    return results[:4]


def run_decision_engine(
    dataset_id: str,
    model_id: str,
    baseline_mode: str,
    scenario_a: Dict[str, Any],
    scenario_b: Optional[Dict[str, Any]] = None,
    reference_index: Optional[int] = None,
    segment_column: Optional[str] = None,
    segment_value: Optional[str] = None,
    language: str = "en",
) -> DecisionEngineResponse:
    lang = "fr" if language == "fr" else "en"
    model_record = store.get_model(model_id)
    enriched_df, dataset_record = build_feature_frame(dataset_id)
    if dataset_id != model_record.dataset_id:
        raise ValueError("Model and dataset do not belong to the same analysis session.")

    feature_columns = model_record.feature_columns
    base_row = build_reference_row(enriched_df, feature_columns, baseline_mode=baseline_mode, reference_index=reference_index)
    available_inputs = _build_available_inputs(base_row, feature_columns, dataset_record.dataframe.copy(), lang)
    segment_candidates = _find_segment_candidates(feature_columns, dataset_record.dataframe.copy())
    if segment_candidates:
        chosen_segment = segment_column if segment_column in segment_candidates else segment_candidates[0]
        chosen_value = segment_value
        if chosen_value is None and chosen_segment in dataset_record.dataframe.columns:
            values = dataset_record.dataframe[chosen_segment].dropna().astype(str).unique().tolist()
            chosen_value = sorted(values)[0] if values else None
        if chosen_value is not None:
            available_inputs.append(
                DecisionInputControl(
                    key="segment_column",
                    label=t("decision_engine.segment_dimension", lang),
                    control_type="selectbox",
                    default_value=chosen_segment,
                    options=segment_candidates,
                )
            )
            available_inputs.append(
                DecisionInputControl(
                    key="segment_value",
                    label=t("decision_engine.segment_value", lang),
                    control_type="selectbox",
                    default_value=chosen_value,
                    options=sorted(dataset_record.dataframe[chosen_segment].dropna().astype(str).unique().tolist()),
                )
            )
    else:
        chosen_segment = None
        chosen_value = None

    scenario_a_changes = normalize_scenario_changes(scenario_a, feature_columns)
    scenario_b_changes = normalize_scenario_changes(scenario_b, feature_columns) if scenario_b else None
    scenario_a_row = _apply_changes(base_row, scenario_a_changes)
    scenario_b_row = _apply_changes(base_row, scenario_b_changes) if scenario_b_changes else None

    baseline_prediction = predict_row(model_id, base_row)
    scenario_a_prediction = predict_row(model_id, scenario_a_row)
    scenario_b_prediction = predict_row(model_id, scenario_b_row) if scenario_b_row is not None else None
    baseline_score = _prediction_score(model_id, base_row)
    scenario_a_score = _prediction_score(model_id, scenario_a_row)
    scenario_b_score = _prediction_score(model_id, scenario_b_row) if scenario_b_row is not None else None

    row_coverage = min(
        row_coverage_pct(base_row),
        row_coverage_pct(scenario_a_row),
        row_coverage_pct(scenario_b_row) if scenario_b_row is not None else 100.0,
    )
    data_size = _data_size_band(len(enriched_df), lang)
    model_reliability = _model_reliability_label(model_record.primary_metric_name, model_record.primary_metric_value, lang)
    confidence_level = _combined_confidence(model_reliability, row_coverage, data_size)

    recommended_decision, prediction_before, prediction_after, delta, delta_pct = _decision_summary(
        baseline_prediction=baseline_prediction,
        scenario_a_prediction=scenario_a_prediction,
        scenario_b_prediction=scenario_b_prediction,
        baseline_score=baseline_score,
        scenario_a_score=scenario_a_score,
        scenario_b_score=scenario_b_score,
        confidence_level=confidence_level,
        task_type=model_record.task_type,
    )

    recommended_row = base_row if recommended_decision == "baseline" else scenario_a_row if recommended_decision == "scenario_a" else scenario_b_row if scenario_b_row is not None else scenario_a_row
    winning_changes = {}
    if recommended_decision == "scenario_a":
        winning_changes = scenario_a_changes
    elif recommended_decision == "scenario_b" and scenario_b_changes:
        winning_changes = scenario_b_changes

    average_row = build_reference_row(enriched_df, feature_columns, baseline_mode="dataset_average")
    average_recommended_row = _apply_changes(average_row, winning_changes)
    average_baseline_prediction = predict_row(model_id, average_row)
    average_recommended_prediction = predict_row(model_id, average_recommended_row)

    impact_views = [
        _impact_view(
            view_key="reference_row",
            label=t("decision_engine.level.reference_row", lang),
            baseline_prediction=baseline_prediction,
            recommended_prediction=prediction_after,
            lang=lang,
        ),
        _impact_view(
            view_key="dataset_average",
            label=t("decision_engine.level.dataset_average", lang),
            baseline_prediction=average_baseline_prediction,
            recommended_prediction=average_recommended_prediction,
            lang=lang,
        ),
    ]

    segment_divergence = False
    if chosen_segment and chosen_value:
        segment_row = _build_segment_row(enriched_df, feature_columns, chosen_segment, chosen_value)
        if segment_row is not None:
            segment_recommended_row = _apply_changes(segment_row, winning_changes)
            segment_baseline_prediction = predict_row(model_id, segment_row)
            segment_recommended_prediction = predict_row(model_id, segment_recommended_row)
            segment_view = _impact_view(
                view_key="segment_level",
                label=f"{t('decision_engine.level.segment_level', lang)}: {chosen_value}",
                baseline_prediction=segment_baseline_prediction,
                recommended_prediction=segment_recommended_prediction,
                lang=lang,
            )
            impact_views.append(segment_view)
            if isinstance(segment_view.delta_pct, float) and isinstance(impact_views[1].delta_pct, float):
                segment_divergence = abs(segment_view.delta_pct - impact_views[1].delta_pct) >= 5.0

    comparison_items = [
        DecisionScenarioComparison(
            scenario_key="baseline",
            prediction=baseline_prediction,
            delta=0.0 if isinstance(baseline_prediction, float) else f"{baseline_prediction} -> {baseline_prediction}",
            delta_pct=0.0 if isinstance(baseline_prediction, float) else None,
        ),
        DecisionScenarioComparison(
            scenario_key="scenario_a",
            prediction=scenario_a_prediction,
            delta=_compute_delta(baseline_prediction, scenario_a_prediction)[0],
            delta_pct=_compute_delta(baseline_prediction, scenario_a_prediction)[1],
        ),
    ]
    if scenario_b_prediction is not None:
        comparison_items.append(
            DecisionScenarioComparison(
                scenario_key="scenario_b",
                prediction=scenario_b_prediction,
                delta=_compute_delta(baseline_prediction, scenario_b_prediction)[0],
                delta_pct=_compute_delta(baseline_prediction, scenario_b_prediction)[1],
            )
        )

    robustness_level = "high"
    if confidence_level == "low" or segment_divergence:
        robustness_level = "low"
    elif confidence_level == "medium" or (isinstance(delta_pct, float) and abs(delta_pct) < 5):
        robustness_level = "medium"

    main_risk = _scenario_risk(winning_changes, row_coverage, model_reliability, lang)
    guardrails = _guardrails(winning_changes, confidence_level=confidence_level, segment_divergence=segment_divergence, lang=lang)
    next_best_analysis = _next_best_analysis(winning_changes or scenario_a_changes, lang)
    missing_useful_data = _missing_data_recommendations(dataset_id, lang)
    risk_summary = (
        "Downside exposure is concentrated where confidence, sample size, or segment consistency are weaker."
        if lang == "en"
        else "L'exposition au risque se concentre la ou la confiance, la taille d'echantillon ou la coherence segmentaire sont plus faibles."
    )

    chart_labels = ["Baseline", "Scenario A"] if lang == "en" else ["Reference", "Scenario A"]
    chart_values = [float(baseline_prediction), float(scenario_a_prediction)] if isinstance(baseline_prediction, float) and isinstance(scenario_a_prediction, float) else []
    delta_pcts = [0.0, _compute_delta(baseline_prediction, scenario_a_prediction)[1]]
    if scenario_b_prediction is not None and isinstance(scenario_b_prediction, float) and chart_values:
        chart_labels.append("Scenario B")
        chart_values.append(float(scenario_b_prediction))
        delta_pcts.append(_compute_delta(baseline_prediction, scenario_b_prediction)[1])
    chart_specs: list[dict[str, Any]] = []
    if chart_values:
        chart_specs.append(
            {
                "key": "scenario_comparison",
                "title": t("decision_engine.chart.scenario_title", lang),
                "figure": build_localized_scenario_comparison_chart(
                    chart_labels,
                    chart_values,
                    delta_pcts,
                    title=t("decision_engine.chart.scenario_title", lang),
                    subtitle=t("decision_engine.chart.scenario_subtitle", lang),
                    winner_label=t("decision_engine.chart.annotation.winner", lang),
                ),
            }
        )
    chart_specs.append(
        {
            "key": "impact_views",
            "title": t("decision_engine.chart.impact_title", lang),
            "figure": build_decision_impact_chart(
                [item.model_dump() for item in impact_views],
                title=t("decision_engine.chart.impact_title", lang),
                subtitle=t("decision_engine.chart.impact_subtitle", lang),
                annotation=t("decision_engine.chart.annotation.impact", lang),
            ),
        }
    )
    risk_items = [
        {"label": item.label, "score": 25 + (abs(float(item.delta_pct or 0.0)) * 3) + (15 if item.view_key == "segment_level" and segment_divergence else 0), "text": item.insight}
        for item in impact_views
    ]
    chart_specs.append(
        {
            "key": "risk_view",
            "title": t("decision_engine.chart.risk_title", lang),
            "figure": build_decision_risk_chart(
                risk_items,
                title=t("decision_engine.chart.risk_title", lang),
                subtitle=t("decision_engine.chart.risk_subtitle", lang),
                annotation=t("decision_engine.chart.annotation.risk", lang),
            ),
        }
    )
    if model_record.top_drivers:
        feature_importance = [{"feature": driver, "importance": max(0.08, 1 - idx * 0.12)} for idx, driver in enumerate(model_record.top_drivers[:5])]
        chart_specs.append(
            {
                "key": "driver_chart",
                "title": "Driver chart" if lang == "en" else "Vue des leviers",
                "figure": build_feature_importance_chart(feature_importance),
            }
        )

    supporting_metrics = {
        model_record.primary_metric_name: model_record.primary_metric_value,
        "row_coverage_pct": row_coverage,
        "baseline_mode": baseline_mode,
    }
    supporting_evidence = [
        f"{_confidence_label(confidence_level, lang)} confidence with {row_coverage:.1f}% row coverage.",
        f"{_robustness_label(robustness_level, lang)} robustness based on consistency across comparison levels.",
        risk_summary,
    ]
    if segment_divergence:
        supporting_evidence.append(
            "Segment sensitivity differs from the global average."
            if lang == "en"
            else "La sensibilite du segment differe de la moyenne globale."
        )

    confidence = DecisionConfidence(
        level=confidence_level,
        model_reliability=model_reliability,
        data_size=data_size,
        row_coverage_pct=row_coverage,
        disclaimer=DISCLAIMER[lang],
    )
    evidence_pack = DecisionEvidencePack(
        supporting_metrics=supporting_metrics,
        top_variables=model_record.top_drivers[:5],
        chart_references=[item["title"] for item in chart_specs],
        scenario_assumptions=[
            "Baseline uses the selected reference mode." if lang == "en" else "La reference utilise le mode de base selectionne.",
            "Scenario changes are directional, not causal." if lang == "en" else "Les changements de scenario sont directionnels, pas causaux.",
        ],
        quality_indicators=[
            f"{t('decision_engine.confidence', lang)}: {_confidence_label(confidence_level, lang)}",
            f"{t('decision_engine.robustness', lang)}: {_robustness_label(robustness_level, lang)}",
            f"{t('decision_engine.simulation_basis', lang)}: {baseline_mode}",
        ],
    )

    recommended_actions = recommend_actions(
        investigation={"insights": []},
        training={
            "top_drivers": model_record.top_drivers,
            "confidence_level": model_record.confidence_level,
        },
        simulation={
            "delta_pct": delta_pct,
            "scenario_a_changes": scenario_a_changes,
            "scenario_b_changes": scenario_b_changes,
            "recommended_decision": recommended_decision,
            "main_risk": main_risk,
        },
    )

    return DecisionEngineResponse(
        baseline_prediction=baseline_prediction,
        scenario_a_prediction=scenario_a_prediction,
        scenario_b_prediction=scenario_b_prediction,
        prediction_before=prediction_before,
        prediction_after=prediction_after,
        delta=delta,
        delta_pct=delta_pct,
        comparison=DecisionComparison(winner=recommended_decision, scenarios=comparison_items),
        recommended_decision=recommended_decision,
        main_risk=main_risk,
        confidence=confidence,
        robustness=robustness_level,  # type: ignore[arg-type]
        guardrails=guardrails,
        key_drivers=model_record.top_drivers[:5],
        supporting_evidence=supporting_evidence,
        missing_useful_data=missing_useful_data,
        next_best_analysis=next_best_analysis,
        simulation_basis_used=f"{baseline_mode} | {chosen_segment or 'none'} | {chosen_value or 'n/a'}",
        impact_views=impact_views,
        risk_summary=risk_summary,
        chart_specs=chart_specs,
        evidence_pack=evidence_pack,
        model_reliability=model_reliability,
        data_size=data_size,
        disclaimer=DISCLAIMER[lang],
        available_inputs=available_inputs,
        scenario_rows=DecisionScenarioRow(
            baseline=_serialize_row(base_row),
            scenario_a=_serialize_row(scenario_a_row),
            scenario_b=_serialize_row(scenario_b_row) if scenario_b_row is not None else None,
        ),
        recommended_actions=recommended_actions,
    )
