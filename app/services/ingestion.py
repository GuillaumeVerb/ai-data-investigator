from __future__ import annotations

from io import BytesIO
from uuid import uuid4

import pandas as pd
from fastapi import UploadFile

from app.core.config import get_settings
from app.core.schemas import UploadResponse
from app.core.state import DatasetRecord, store


def _normalize_column(name: str) -> str:
    normalized = name.strip().lower().replace(" ", "_")
    return "".join(ch for ch in normalized if ch.isalnum() or ch == "_")


def _clean_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()
    df.columns = [_normalize_column(str(col)) for col in df.columns]

    for column in df.columns:
        if df[column].dtype == "object":
            try:
                parsed = pd.to_datetime(df[column], errors="raise")
            except (ValueError, TypeError):
                continue
            if parsed.notna().mean() > 0.8:
                df[column] = parsed

    return df


async def load_upload(file: UploadFile) -> UploadResponse:
    content = await file.read()
    dataframe = pd.read_csv(BytesIO(content))
    dataframe = _clean_dataframe(dataframe)

    dataset_id = str(uuid4())
    store.save_dataset(
        DatasetRecord(
            dataset_id=dataset_id,
            filename=file.filename or "uploaded.csv",
            dataframe=dataframe,
        )
    )

    settings = get_settings()
    preview = dataframe.head(settings.max_preview_rows).copy()
    preview = preview.astype(object).where(pd.notnull(preview), None)

    return UploadResponse(
        dataset_id=dataset_id,
        filename=file.filename or "uploaded.csv",
        rows=int(dataframe.shape[0]),
        columns=int(dataframe.shape[1]),
        preview=preview.to_dict(orient="records"),
    )


def load_sample_dataset(file_path: str) -> UploadResponse:
    dataframe = pd.read_csv(file_path)
    dataframe = _clean_dataframe(dataframe)
    dataset_id = str(uuid4())
    store.save_dataset(
        DatasetRecord(
            dataset_id=dataset_id,
            filename=file_path.split("/")[-1],
            dataframe=dataframe,
        )
    )

    settings = get_settings()
    preview = dataframe.head(settings.max_preview_rows).copy()
    preview = preview.astype(object).where(pd.notnull(preview), None)
    return UploadResponse(
        dataset_id=dataset_id,
        filename=file_path.split("/")[-1],
        rows=int(dataframe.shape[0]),
        columns=int(dataframe.shape[1]),
        preview=preview.to_dict(orient="records"),
    )
