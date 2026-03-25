from __future__ import annotations

from app.core.schemas import JoinAssistantResponse, JoinCandidate
from app.core.state import store
from app.services.dataset_merge import preview_merge


def analyze_join_candidates(dataset_id: str, language: str = "en") -> JoinAssistantResponse:
    base = store.get_dataset(dataset_id)
    candidates: list[JoinCandidate] = []
    for item in store.list_datasets():
        if item.dataset_id == dataset_id:
            continue
        preview = preview_merge(dataset_id, item.dataset_id)
        candidates.append(
            JoinCandidate(
                right_dataset_id=item.dataset_id,
                filename=item.filename,
                suggested_join_keys=preview.suggested_join_keys,
                merge_readiness=preview.merge_readiness,
                estimated_overlap_rows=preview.estimated_overlap_rows,
                business_value=preview.business_value,
                explanation=preview.explanation,
                compatibility_warnings=preview.compatibility_warnings,
            )
        )

    candidates.sort(
        key=lambda item: (
            {"high": 0, "medium": 1, "low": 2}[item.merge_readiness],
            -item.estimated_overlap_rows,
        )
    )

    if candidates:
        top = candidates[0]
        recommended_next_step = (
            f"Join {base.filename} with {top.filename} on {', '.join(top.suggested_join_keys or ['the suggested shared keys'])}."
            if language == "en"
            else f"Joindre {base.filename} avec {top.filename} sur {', '.join(top.suggested_join_keys or ['les cles partagees suggerees'])}."
        )
    else:
        recommended_next_step = (
            "Load a second dataset to activate the join assistant."
            if language == "en"
            else "Charge un second dataset pour activer le join assistant."
        )

    return JoinAssistantResponse(
        dataset_id=dataset_id,
        candidates=candidates[:4],
        recommended_next_step=recommended_next_step,
    )
