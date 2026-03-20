from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pandas as pd

from app.core.schemas import CopilotSessionState, DatasetListItem


@dataclass
class DatasetRecord:
    dataset_id: str
    filename: str
    dataframe: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelRecord:
    model_id: str
    dataset_id: str
    target: str
    task_type: str
    pipeline: Any
    feature_columns: List[str]
    reference_row: Dict[str, Any]
    metrics: Dict[str, float]
    primary_metric_name: str
    primary_metric_value: float
    confidence_level: str
    data_coverage_pct: float
    top_drivers: List[str] = field(default_factory=list)


@dataclass
class CopilotSessionRecord:
    session_id: str
    active_dataset_id: Optional[str] = None
    active_model_id: Optional[str] = None
    last_question: Optional[str] = None
    last_intent: Optional[str] = None
    last_summary: Optional[str] = None
    last_simulation: Optional[str] = None
    latest_investigation_titles: List[str] = field(default_factory=list)
    latest_recommended_actions: List[str] = field(default_factory=list)
    message_history: List[str] = field(default_factory=list)

    def to_schema(self) -> CopilotSessionState:
        return CopilotSessionState(
            session_id=self.session_id,
            active_dataset_id=self.active_dataset_id,
            active_model_id=self.active_model_id,
            last_question=self.last_question,
            last_intent=self.last_intent,
            last_summary=self.last_summary,
            last_simulation=self.last_simulation,
            latest_investigation_titles=self.latest_investigation_titles,
            latest_recommended_actions=self.latest_recommended_actions,
            message_history=self.message_history,
        )


class InMemoryStore:
    def __init__(self) -> None:
        self.datasets: Dict[str, DatasetRecord] = {}
        self.models: Dict[str, ModelRecord] = {}
        self.copilot_sessions: Dict[str, CopilotSessionRecord] = {}

    def save_dataset(self, record: DatasetRecord) -> None:
        self.datasets[record.dataset_id] = record

    def get_dataset(self, dataset_id: str) -> DatasetRecord:
        return self.datasets[dataset_id]

    def list_datasets(self) -> List[DatasetListItem]:
        return [
            DatasetListItem(
                dataset_id=record.dataset_id,
                filename=record.filename,
                rows=int(record.dataframe.shape[0]),
                columns=int(record.dataframe.shape[1]),
            )
            for record in self.datasets.values()
        ]

    def save_model(self, record: ModelRecord) -> None:
        self.models[record.model_id] = record

    def get_model(self, model_id: str) -> ModelRecord:
        return self.models[model_id]

    def get_or_create_session(self, session_id: Optional[str] = None, dataset_id: Optional[str] = None) -> CopilotSessionRecord:
        if session_id and session_id in self.copilot_sessions:
            return self.copilot_sessions[session_id]

        new_session_id = session_id or str(uuid4())
        record = CopilotSessionRecord(session_id=new_session_id, active_dataset_id=dataset_id)
        self.copilot_sessions[new_session_id] = record
        return record

    def reset_session(self, session_id: str, dataset_id: Optional[str] = None) -> CopilotSessionState:
        record = CopilotSessionRecord(session_id=session_id, active_dataset_id=dataset_id)
        self.copilot_sessions[session_id] = record
        return record.to_schema()


store = InMemoryStore()
