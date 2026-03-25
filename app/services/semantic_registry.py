from __future__ import annotations

from app.core.schemas import SemanticKpiDefinition, SemanticKpiRegistryResponse
from app.core.state import store


def build_kpi_registry(dataset_id: str, language: str = "en") -> SemanticKpiRegistryResponse:
    df = store.get_dataset(dataset_id).dataframe
    kpis: list[SemanticKpiDefinition] = []
    if "revenue" in df.columns:
        kpis.append(
            SemanticKpiDefinition(
                name="Revenue",
                formula="SUM(revenue)",
                business_use="Track topline commercial performance." if language == "en" else "Suivre la performance commerciale de topline.",
                grain="date / region / product",
            )
        )
    if {"revenue", "units_sold"}.issubset(df.columns):
        kpis.append(
            SemanticKpiDefinition(
                name="Average revenue per unit",
                formula="SUM(revenue) / SUM(units_sold)",
                business_use="Separate price/mix effects from pure volume." if language == "en" else "Dissocier les effets prix/mix du pur volume.",
                grain="segment / product / region",
            )
        )
    if {"revenue", "marketing_spend"}.issubset(df.columns):
        kpis.append(
            SemanticKpiDefinition(
                name="Marketing efficiency",
                formula="SUM(revenue) / SUM(marketing_spend)",
                business_use="Assess return on commercial investment." if language == "en" else "Evaluer le rendement de l investissement commercial.",
                grain="channel / campaign / region",
            )
        )
    if "qualified_pipeline" in df.columns:
        kpis.append(
            SemanticKpiDefinition(
                name="Qualified pipeline",
                formula="SUM(qualified_pipeline)",
                business_use="Track pipeline creation quality and scale." if language == "en" else "Suivre la qualite et le volume de pipeline cree.",
                grain="campaign / date / region",
            )
        )
    default_kpi = kpis[0].name if kpis else ("Main KPI" if language == "en" else "KPI principal")
    return SemanticKpiRegistryResponse(dataset_id=dataset_id, kpis=kpis, recommended_default_kpi=default_kpi)
