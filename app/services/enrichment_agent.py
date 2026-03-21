from __future__ import annotations

from typing import List

from app.core.schemas import EnrichmentResponse, EnrichmentSuggestion
from app.core.state import store


def suggest_enrichment(dataset_id: str) -> EnrichmentResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe

    suggestions: List[EnrichmentSuggestion] = []
    columns = set(df.columns)
    temporal = set(df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist())

    if temporal:
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="Marketing campaigns",
                why_it_matters="Campaign timing can explain spikes or drops that are invisible in transactional data alone.",
                integration_hint="Join campaign logs by date and channel, then compare campaign periods versus non-campaign periods.",
                expected_value="Better attribution of demand changes and stronger scenario recommendations.",
                likely_join_key="date",
                business_question_helped="Improves diagnosis of revenue changes, marketing efficiency, and scenario reliability.",
            )
        )
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="External calendar factors",
                why_it_matters="Holidays, promotions, and seasonality often distort trends and should be separated from core demand.",
                integration_hint="Join a calendar table by date with holiday flags, season markers, and special-event labels.",
                expected_value="Cleaner trend interpretation and more credible root-cause explanations.",
                likely_join_key="date",
                business_question_helped="Improves trend analysis, anomaly interpretation, and forecasting stability.",
            )
        )

    if "customer_segment" not in columns:
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="Customer segmentation data",
                why_it_matters="Without segment attributes, it is hard to know which audiences drive or drag performance.",
                integration_hint="Join customer segment or account tier data on customer or account identifiers before retraining models.",
                expected_value="Sharper targeting, better recommendations, and clearer driver analysis.",
                likely_join_key="customer_id",
                business_question_helped="Improves prioritization, segment analysis, and action recommendations.",
            )
        )

    if "region" in columns and "product" in columns:
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="Inventory or supply constraints",
                why_it_matters="Regional underperformance may come from stock availability rather than demand weakness.",
                integration_hint="Join inventory snapshots by date, product, and region to identify operational bottlenecks.",
                expected_value="More accurate diagnosis of whether issues are commercial or operational.",
                likely_join_key="date, product, region",
                business_question_helped="Improves root-cause analysis and protects decision quality before rollout.",
            )
        )

    if "price" in columns and "product" in columns:
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="Competitor pricing",
                why_it_matters="Relative pricing pressure often explains demand shifts better than internal price alone.",
                integration_hint="Join competitor pricing by date and product, then compare internal price index versus market price index.",
                expected_value="Stronger pricing decisions and more credible elasticity analysis.",
                likely_join_key="date, product",
                business_question_helped="Improves pricing scenarios, prioritization, and decision guardrails.",
            )
        )

    return EnrichmentResponse(dataset_id=dataset_id, suggestions=suggestions[:4])
