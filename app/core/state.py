from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pandas as pd

from app.core.config import get_settings
from app.core.schemas import (
    ApprovalItem,
    ConnectorItem,
    CopilotSessionState,
    DatasetListItem,
    ExportArtifactItem,
    OperationLogItem,
    ProjectItem,
    UserItem,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


@dataclass
class OperationLogRecord:
    tool_name: str
    status: str
    route: str
    detail: str
    dataset_id: Optional[str] = None
    latency_ms: Optional[int] = None

    def to_schema(self) -> OperationLogItem:
        return OperationLogItem(
            tool_name=self.tool_name,
            status=self.status,
            route=self.route,
            detail=self.detail,
            dataset_id=self.dataset_id,
            latency_ms=self.latency_ms,
        )


@dataclass
class UserRecord:
    user_id: str
    name: str
    email: Optional[str]
    role: str
    created_at: str

    def to_schema(self) -> UserItem:
        return UserItem(
            user_id=self.user_id,
            name=self.name,
            email=self.email,
            role=self.role,
            created_at=self.created_at,
        )


@dataclass
class ProjectRecord:
    project_id: str
    name: str
    description: Optional[str]
    owner_user_id: Optional[str]
    created_at: str

    def to_schema(self) -> ProjectItem:
        return ProjectItem(
            project_id=self.project_id,
            name=self.name,
            description=self.description,
            owner_user_id=self.owner_user_id,
            created_at=self.created_at,
        )


@dataclass
class ConnectorRecord:
    connector_id: str
    name: str
    connector_type: str
    config: Dict[str, Any]
    project_id: Optional[str]
    created_by: Optional[str]
    created_at: str

    def to_schema(self) -> ConnectorItem:
        summary_parts = []
        if self.connector_type == "csv_url":
            summary_parts.append(self.config.get("url", ""))
        if self.connector_type == "sqlite":
            summary_parts.append(self.config.get("path", ""))
            if self.config.get("table"):
                summary_parts.append(f"table={self.config['table']}")
        return ConnectorItem(
            connector_id=self.connector_id,
            name=self.name,
            connector_type=self.connector_type,
            project_id=self.project_id,
            created_by=self.created_by,
            created_at=self.created_at,
            config_summary=" | ".join(part for part in summary_parts if part),
        )


@dataclass
class ApprovalRecord:
    approval_id: str
    title: str
    object_type: str
    object_id: Optional[str]
    summary: str
    status: str
    project_id: Optional[str]
    requested_by: Optional[str]
    reviewer: Optional[str]
    comment: Optional[str]
    created_at: str
    updated_at: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_schema(self) -> ApprovalItem:
        return ApprovalItem(
            approval_id=self.approval_id,
            title=self.title,
            object_type=self.object_type,
            object_id=self.object_id,
            summary=self.summary,
            status=self.status,
            project_id=self.project_id,
            requested_by=self.requested_by,
            reviewer=self.reviewer,
            comment=self.comment,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


@dataclass
class ExportArtifactRecord:
    artifact_id: str
    artifact_type: str
    name: str
    created_at: str
    project_id: Optional[str]
    created_by: Optional[str]
    summary: str
    content: Dict[str, Any] = field(default_factory=dict)

    def to_schema(self) -> ExportArtifactItem:
        return ExportArtifactItem(
            artifact_id=self.artifact_id,
            artifact_type=self.artifact_type,
            name=self.name,
            created_at=self.created_at,
            project_id=self.project_id,
            created_by=self.created_by,
            summary=self.summary,
        )


class InMemoryStore:
    def __init__(self, runtime_state_path: str) -> None:
        self.runtime_state_path = Path(runtime_state_path)
        self.datasets: Dict[str, DatasetRecord] = {}
        self.models: Dict[str, ModelRecord] = {}
        self.copilot_sessions: Dict[str, CopilotSessionRecord] = {}
        self.operation_logs: List[OperationLogRecord] = []
        self.users: Dict[str, UserRecord] = {}
        self.projects: Dict[str, ProjectRecord] = {}
        self.connectors: Dict[str, ConnectorRecord] = {}
        self.approvals: Dict[str, ApprovalRecord] = {}
        self.exports: Dict[str, ExportArtifactRecord] = {}
        self._load_runtime_state()

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

    def log_operation(
        self,
        *,
        tool_name: str,
        status: str,
        route: str,
        detail: str,
        dataset_id: Optional[str] = None,
        latency_ms: Optional[int] = None,
    ) -> None:
        self.operation_logs = [
            OperationLogRecord(
                tool_name=tool_name,
                status=status,
                route=route,
                detail=detail,
                dataset_id=dataset_id,
                latency_ms=latency_ms,
            ),
            *self.operation_logs,
        ][:50]
        self._save_runtime_state()

    def list_operation_logs(self) -> List[OperationLogItem]:
        return [item.to_schema() for item in self.operation_logs]

    def create_user(self, name: str, email: Optional[str], role: str) -> UserItem:
        user = UserRecord(
            user_id=str(uuid4()),
            name=name,
            email=email,
            role=role,
            created_at=_utc_now(),
        )
        self.users[user.user_id] = user
        self._save_runtime_state()
        return user.to_schema()

    def list_users(self) -> List[UserItem]:
        return [user.to_schema() for user in sorted(self.users.values(), key=lambda item: item.created_at, reverse=True)]

    def create_project(self, name: str, description: Optional[str], owner_user_id: Optional[str]) -> ProjectItem:
        project = ProjectRecord(
            project_id=str(uuid4()),
            name=name,
            description=description,
            owner_user_id=owner_user_id,
            created_at=_utc_now(),
        )
        self.projects[project.project_id] = project
        self._save_runtime_state()
        return project.to_schema()

    def list_projects(self) -> List[ProjectItem]:
        return [project.to_schema() for project in sorted(self.projects.values(), key=lambda item: item.created_at, reverse=True)]

    def create_connector(
        self,
        *,
        name: str,
        connector_type: str,
        config: Dict[str, Any],
        project_id: Optional[str],
        created_by: Optional[str],
    ) -> ConnectorItem:
        connector = ConnectorRecord(
            connector_id=str(uuid4()),
            name=name,
            connector_type=connector_type,
            config=config,
            project_id=project_id,
            created_by=created_by,
            created_at=_utc_now(),
        )
        self.connectors[connector.connector_id] = connector
        self._save_runtime_state()
        return connector.to_schema()

    def get_connector_record(self, connector_id: str) -> ConnectorRecord:
        return self.connectors[connector_id]

    def list_connectors(self) -> List[ConnectorItem]:
        return [connector.to_schema() for connector in sorted(self.connectors.values(), key=lambda item: item.created_at, reverse=True)]

    def create_approval(
        self,
        *,
        title: str,
        object_type: str,
        object_id: Optional[str],
        summary: str,
        project_id: Optional[str],
        requested_by: Optional[str],
        payload: Optional[Dict[str, Any]] = None,
    ) -> ApprovalItem:
        now = _utc_now()
        approval = ApprovalRecord(
            approval_id=str(uuid4()),
            title=title,
            object_type=object_type,
            object_id=object_id,
            summary=summary,
            status="pending",
            project_id=project_id,
            requested_by=requested_by,
            reviewer=None,
            comment=None,
            created_at=now,
            updated_at=now,
            payload=payload or {},
        )
        self.approvals[approval.approval_id] = approval
        self._save_runtime_state()
        return approval.to_schema()

    def decide_approval(self, approval_id: str, decision: str, reviewer: Optional[str], comment: Optional[str]) -> ApprovalItem:
        approval = self.approvals[approval_id]
        approval.status = decision
        approval.reviewer = reviewer
        approval.comment = comment
        approval.updated_at = _utc_now()
        self._save_runtime_state()
        return approval.to_schema()

    def list_approvals(self) -> List[ApprovalItem]:
        return [approval.to_schema() for approval in sorted(self.approvals.values(), key=lambda item: item.updated_at, reverse=True)]

    def create_export_artifact(
        self,
        *,
        artifact_type: str,
        name: str,
        summary: str,
        content: Dict[str, Any],
        project_id: Optional[str],
        created_by: Optional[str],
    ) -> ExportArtifactRecord:
        artifact = ExportArtifactRecord(
            artifact_id=str(uuid4()),
            artifact_type=artifact_type,
            name=name,
            created_at=_utc_now(),
            project_id=project_id,
            created_by=created_by,
            summary=summary,
            content=content,
        )
        self.exports[artifact.artifact_id] = artifact
        self._save_runtime_state()
        return artifact

    def list_exports(self) -> List[ExportArtifactItem]:
        return [artifact.to_schema() for artifact in sorted(self.exports.values(), key=lambda item: item.created_at, reverse=True)]

    def _runtime_payload(self) -> Dict[str, Any]:
        return {
            "users": [user.__dict__ for user in self.users.values()],
            "projects": [project.__dict__ for project in self.projects.values()],
            "connectors": [connector.__dict__ for connector in self.connectors.values()],
            "approvals": [approval.__dict__ for approval in self.approvals.values()],
            "exports": [artifact.__dict__ for artifact in self.exports.values()],
            "operation_logs": [log.__dict__ for log in self.operation_logs],
        }

    def _save_runtime_state(self) -> None:
        self.runtime_state_path.parent.mkdir(parents=True, exist_ok=True)
        self.runtime_state_path.write_text(json.dumps(self._runtime_payload(), ensure_ascii=True, indent=2), encoding="utf-8")

    def _load_runtime_state(self) -> None:
        if not self.runtime_state_path.exists():
            return
        try:
            payload = json.loads(self.runtime_state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        self.users = {
            item["user_id"]: UserRecord(**item)
            for item in payload.get("users", [])
        }
        self.projects = {
            item["project_id"]: ProjectRecord(**item)
            for item in payload.get("projects", [])
        }
        self.connectors = {
            item["connector_id"]: ConnectorRecord(**item)
            for item in payload.get("connectors", [])
        }
        self.approvals = {
            item["approval_id"]: ApprovalRecord(**item)
            for item in payload.get("approvals", [])
        }
        self.exports = {
            item["artifact_id"]: ExportArtifactRecord(**item)
            for item in payload.get("exports", [])
        }
        self.operation_logs = [OperationLogRecord(**item) for item in payload.get("operation_logs", [])[:50]]


store = InMemoryStore(get_settings().runtime_state_path)
