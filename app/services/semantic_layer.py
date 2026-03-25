from __future__ import annotations

import pandas as pd

from app.core.schemas import SemanticLayerResponse
from app.core.state import store


def build_semantic_layer(dataset_id: str, language: str = "en") -> SemanticLayerResponse:
    df = store.get_dataset(dataset_id).dataframe.copy()
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    time_dimensions = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    dimensions = [col for col in df.columns if col not in numeric_columns and col not in time_dimensions][:8]

    entities = []
    if "customer_segment" in df.columns:
        entities.append("customer_segment")
    if "product" in df.columns:
        entities.append("product")
    if "region" in df.columns:
        entities.append("region")
    if "channel" in df.columns:
        entities.append("channel")

    measures = [col for col in numeric_columns if pd.api.types.is_numeric_dtype(df[col])][:8]
    recommended_kpis: list[str] = []
    if "revenue" in df.columns:
        recommended_kpis.append("Total revenue")
    if "units_sold" in df.columns:
        recommended_kpis.append("Units sold")
    if {"revenue", "units_sold"}.issubset(df.columns):
        recommended_kpis.append("Average revenue per unit")
    if {"revenue", "marketing_spend"}.issubset(df.columns):
        recommended_kpis.append("Revenue to marketing efficiency")
    if "qualified_pipeline" in df.columns:
        recommended_kpis.append("Qualified pipeline")
    if "conversions" in df.columns:
        recommended_kpis.append("Conversions")

    if language == "fr":
        question_templates = [
            "Quel segment contribue le plus a la performance ?",
            "Quelles dimensions expliquent les variations du KPI principal ?",
            "Quel est le bon niveau de prix ou de spend a tester ensuite ?",
        ]
    else:
        question_templates = [
            "Which segment contributes most to performance?",
            "Which dimensions explain changes in the main KPI?",
            "What pricing or spend scenario should be tested next?",
        ]

    return SemanticLayerResponse(
        dataset_id=dataset_id,
        entities=entities,
        dimensions=dimensions,
        time_dimensions=time_dimensions[:4],
        measures=measures,
        recommended_kpis=recommended_kpis[:6],
        business_questions=question_templates,
    )
