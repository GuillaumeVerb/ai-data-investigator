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
            )
        )
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="External calendar factors",
                why_it_matters="Holidays, promotions, and seasonality often distort trends and should be separated from core demand.",
                integration_hint="Join a calendar table by date with holiday flags, season markers, and special-event labels.",
                expected_value="Cleaner trend interpretation and more credible root-cause explanations.",
            )
        )

    if "customer_segment" not in columns:
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="Customer segmentation data",
                why_it_matters="Without segment attributes, it is hard to know which audiences drive or drag performance.",
                integration_hint="Join customer segment or account tier data on customer or account identifiers before retraining models.",
                expected_value="Sharper targeting, better recommendations, and clearer driver analysis.",
            )
        )

    if "region" in columns and "product" in columns:
        suggestions.append(
            EnrichmentSuggestion(
                dataset_name="Inventory or supply constraints",
                why_it_matters="Regional underperformance may come from stock availability rather than demand weakness.",
                integration_hint="Join inventory snapshots by date, product, and region to identify operational bottlenecks.",
                expected_value="More accurate diagnosis of whether issues are commercial or operational.",
            )
        )

    return EnrichmentResponse(dataset_id=dataset_id, suggestions=suggestions[:4])
