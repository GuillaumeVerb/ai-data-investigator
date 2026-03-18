from __future__ import annotations

from typing import List

import pandas as pd

from app.core.schemas import MergePreviewResponse
from app.core.state import store


PREFERRED_JOIN_KEYS = ["date", "product", "region"]


def preview_merge(left_dataset_id: str, right_dataset_id: str, join_keys: List[str] | None = None) -> MergePreviewResponse:
    left = store.get_dataset(left_dataset_id)
    right = store.get_dataset(right_dataset_id)

    shared_columns = sorted(set(left.dataframe.columns).intersection(right.dataframe.columns))
    suggested_join_keys = join_keys or [key for key in PREFERRED_JOIN_KEYS if key in shared_columns]
    if not suggested_join_keys and shared_columns:
        suggested_join_keys = shared_columns[:1]

    if suggested_join_keys:
        left_keys = left.dataframe[suggested_join_keys].astype(str)
        right_keys = right.dataframe[suggested_join_keys].astype(str)
        left_composite = left_keys.agg("||".join, axis=1)
        right_composite = right_keys.agg("||".join, axis=1)
        overlap = int(left_composite.isin(set(right_composite)).sum())
        preview = pd.merge(
            left.dataframe.head(20),
            right.dataframe.head(20),
            on=suggested_join_keys,
            how="inner",
            suffixes=("_left", "_right"),
        ).head(5)
    else:
        overlap = 0
        preview = pd.DataFrame()

    readiness = "high" if overlap >= 5 else "medium" if overlap >= 1 else "low"
    explanation = (
        f"Shared columns: {', '.join(shared_columns) if shared_columns else 'none'}. "
        f"Suggested join keys: {', '.join(suggested_join_keys) if suggested_join_keys else 'none'}. "
        f"Estimated overlap rows: {overlap}."
    )
    preview = preview.astype(object).where(pd.notnull(preview), None) if not preview.empty else preview

    return MergePreviewResponse(
        left_dataset_id=left_dataset_id,
        right_dataset_id=right_dataset_id,
        suggested_join_keys=suggested_join_keys,
        available_shared_columns=shared_columns,
        estimated_overlap_rows=overlap,
        left_rows=int(left.dataframe.shape[0]),
        right_rows=int(right.dataframe.shape[0]),
        merge_readiness=readiness,
        explanation=explanation,
        preview=preview.to_dict(orient="records") if not preview.empty else [],
    )
