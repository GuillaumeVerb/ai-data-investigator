from __future__ import annotations

from app.core.schemas import PreparationAgentResponse, PreparationTask
from app.core.state import store
from app.services.enrichment_agent import suggest_enrichment
from app.services.feature_engineering import build_derived_features


def build_preparation_plan(dataset_id: str, language: str = "en") -> PreparationAgentResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe.copy()
    _, derived_features, derived_feature_details = build_derived_features(df)
    enrichment = suggest_enrichment(dataset_id, language)

    cleanup_tasks: list[PreparationTask] = []
    typed_columns = {column: str(dtype) for column, dtype in df.dtypes.items()}
    missing_pct = (df.isna().mean() * 100).round(2).to_dict()

    high_missing = [col for col, pct in missing_pct.items() if pct >= 20]
    for column in high_missing[:3]:
        cleanup_tasks.append(
            PreparationTask(
                title=(f"Prioritize missing-value treatment for {column}" if language == "en" else f"Prioriser le traitement des valeurs manquantes pour {column}"),
                rationale=(
                    f"{column} has {missing_pct[column]}% missing values and can weaken downstream modeling."
                    if language == "en"
                    else f"{column} presente {missing_pct[column]}% de valeurs manquantes et peut fragiliser la modelisation."
                ),
                priority="high",
            )
        )

    object_columns = [column for column, dtype in typed_columns.items() if dtype == "object"]
    for column in object_columns[:2]:
        cleanup_tasks.append(
            PreparationTask(
                title=(f"Review categorical normalization for {column}" if language == "en" else f"Verifier la normalisation categorielle pour {column}"),
                rationale=(
                    "Free-text or inconsistent category values can create noisy signals."
                    if language == "en"
                    else "Des valeurs categorielles libres ou incoherentes peuvent creer des signaux bruyants."
                ),
                priority="medium",
            )
        )

    feature_opportunities = [
        PreparationTask(
            title=(
                f"Create feature: {item['feature']}" if language == "en" else f"Creer la feature : {item['feature']}"
            ),
            rationale=item["reason"],
            priority="medium" if idx > 1 else "high",
        )
        for idx, item in enumerate(derived_feature_details[:5])
    ]

    enrichment_priorities = [
        PreparationTask(
            title=item.dataset_name,
            rationale=item.why_it_matters,
            priority="medium" if idx else "high",
        )
        for idx, item in enumerate(enrichment.suggestions[:3])
    ]

    readiness_score = round(
        max(
            0.0,
            min(
                100.0,
                100 - sum(missing_pct.values()) / max(len(missing_pct), 1) * 0.7 + min(len(derived_features), 8) * 2,
            ),
        ),
        1,
    )
    recommended_next_step = (
        "Stabilize column quality first, then add the top derived features before training."
        if language == "en"
        else "Stabilise d'abord la qualite des colonnes, puis ajoute les features derivees prioritaires avant l'entrainement."
    )

    return PreparationAgentResponse(
        dataset_id=dataset_id,
        typed_columns=typed_columns,
        cleanup_tasks=cleanup_tasks[:5],
        feature_opportunities=feature_opportunities,
        enrichment_priorities=enrichment_priorities,
        readiness_score=readiness_score,
        recommended_next_step=recommended_next_step,
    )
