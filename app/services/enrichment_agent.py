from __future__ import annotations

from typing import List

from app.core.schemas import EnrichmentResponse, EnrichmentSuggestion
from app.core.state import store


def suggest_enrichment(dataset_id: str, language: str = "en") -> EnrichmentResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe
    lang = "fr" if language == "fr" else "en"

    suggestions: List[EnrichmentSuggestion] = []
    columns = set(df.columns)
    temporal = set(df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist())

    if temporal:
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="Marketing campaigns",
                why_it_matters=(
                    "Campaign timing can explain spikes or drops that are invisible in transactional data alone."
                    if lang == "en"
                    else "Le calendrier des campagnes peut expliquer des pics ou des baisses invisibles dans les seules donnees transactionnelles."
                ),
                integration_hint=(
                    "Join campaign logs by date and channel, then compare campaign periods versus non-campaign periods."
                    if lang == "en"
                    else "Joindre les campagnes par date et canal, puis comparer les periodes de campagne aux periodes hors campagne."
                ),
                expected_value=(
                    "Better attribution of demand changes and stronger scenario recommendations."
                    if lang == "en"
                    else "Une meilleure attribution des variations de demande et des recommandations de scenario plus solides."
                ),
                likely_join_key="date",
                business_question_helped=(
                    "Improves diagnosis of revenue changes, marketing efficiency, and scenario reliability."
                    if lang == "en"
                    else "Ameliore le diagnostic des variations de revenu, l'efficacite marketing et la fiabilite des scenarios."
                ),
            )
        )
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="External calendar factors" if lang == "en" else "Facteurs calendaires externes",
                why_it_matters=(
                    "Holidays, promotions, and seasonality often distort trends and should be separated from core demand."
                    if lang == "en"
                    else "Les jours feries, promotions et effets de saisonnalite perturbent souvent les tendances et doivent etre separes de la demande de fond."
                ),
                integration_hint=(
                    "Join a calendar table by date with holiday flags, season markers, and special-event labels."
                    if lang == "en"
                    else "Joindre une table calendrier par date avec indicateurs de jours feries, saison et evenements speciaux."
                ),
                expected_value=(
                    "Cleaner trend interpretation and more credible root-cause explanations."
                    if lang == "en"
                    else "Une interpretation plus propre des tendances et des explications de cause racine plus credibles."
                ),
                likely_join_key="date",
                business_question_helped=(
                    "Improves trend analysis, anomaly interpretation, and forecasting stability."
                    if lang == "en"
                    else "Ameliore l'analyse des tendances, l'interpretation des anomalies et la stabilite des previsions."
                ),
            )
        )

    if "customer_segment" not in columns:
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="Customer segmentation data" if lang == "en" else "Donnees de segmentation client",
                why_it_matters=(
                    "Without segment attributes, it is hard to know which audiences drive or drag performance."
                    if lang == "en"
                    else "Sans attributs de segment, il est difficile de savoir quels publics soutiennent ou freinent la performance."
                ),
                integration_hint=(
                    "Join customer segment or account tier data on customer or account identifiers before retraining models."
                    if lang == "en"
                    else "Joindre des donnees de segment client ou de tier de compte sur des identifiants client ou compte avant de re-entrainer les modeles."
                ),
                expected_value=(
                    "Sharper targeting, better recommendations, and clearer driver analysis."
                    if lang == "en"
                    else "Un ciblage plus precis, de meilleures recommandations et une analyse des leviers plus claire."
                ),
                likely_join_key="customer_id",
                business_question_helped=(
                    "Improves prioritization, segment analysis, and action recommendations."
                    if lang == "en"
                    else "Ameliore la priorisation, l'analyse par segment et les recommandations d'action."
                ),
            )
        )

    if "region" in columns and "product" in columns:
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="Inventory or supply constraints" if lang == "en" else "Contraintes de stock ou de supply",
                why_it_matters=(
                    "Regional underperformance may come from stock availability rather than demand weakness."
                    if lang == "en"
                    else "Une sous-performance regionale peut venir de la disponibilite produit plutot que d'une faiblesse de la demande."
                ),
                integration_hint=(
                    "Join inventory snapshots by date, product, and region to identify operational bottlenecks."
                    if lang == "en"
                    else "Joindre des snapshots de stock par date, produit et region pour identifier les goulets operationnels."
                ),
                expected_value=(
                    "More accurate diagnosis of whether issues are commercial or operational."
                    if lang == "en"
                    else "Un diagnostic plus precis pour distinguer les problemes commerciaux des problemes operationnels."
                ),
                likely_join_key="date, product, region",
                business_question_helped=(
                    "Improves root-cause analysis and protects decision quality before rollout."
                    if lang == "en"
                    else "Ameliore l'analyse de cause racine et protege la qualite de la decision avant de deployer."
                ),
            )
        )

    if "price" in columns and "product" in columns:
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="Competitor pricing" if lang == "en" else "Prix concurrents",
                why_it_matters=(
                    "Relative pricing pressure often explains demand shifts better than internal price alone."
                    if lang == "en"
                    else "La pression tarifaire relative explique souvent mieux les variations de demande que le seul prix interne."
                ),
                integration_hint=(
                    "Join competitor pricing by date and product, then compare internal price index versus market price index."
                    if lang == "en"
                    else "Joindre les prix concurrents par date et produit, puis comparer l'indice de prix interne a l'indice de prix du marche."
                ),
                expected_value=(
                    "Stronger pricing decisions and more credible elasticity analysis."
                    if lang == "en"
                    else "Des decisions pricing plus solides et une analyse d'elasticite plus credible."
                ),
                likely_join_key="date, product",
                business_question_helped=(
                    "Improves pricing scenarios, prioritization, and decision guardrails."
                    if lang == "en"
                    else "Ameliore les scenarios de prix, la priorisation et les garde-fous de decision."
                ),
            )
        )

    return EnrichmentResponse(dataset_id=dataset_id, suggestions=suggestions[:4])
