from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class DatasetRecord:
    dataset_id: str
    filename: str
    dataframe: pd.DataFrame
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelRecord:
    model_id: str
    dataset_id: str
    target: str
    task_type: str
    pipeline: Any
    feature_columns: list[str]
    reference_row: dict[str, Any]


class InMemoryStore:
    def __init__(self) -> None:
        self.datasets: dict[str, DatasetRecord] = {}
        self.models: dict[str, ModelRecord] = {}

    def save_dataset(self, record: DatasetRecord) -> None:
        self.datasets[record.dataset_id] = record

    def get_dataset(self, dataset_id: str) -> DatasetRecord:
        return self.datasets[dataset_id]

    def save_model(self, record: ModelRecord) -> None:
        self.models[record.model_id] = record

    def get_model(self, model_id: str) -> ModelRecord:
        return self.models[model_id]


store = InMemoryStore()
