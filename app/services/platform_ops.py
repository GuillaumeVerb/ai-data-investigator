from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

import pandas as pd

from app.core.config import get_settings
from app.core.schemas import (
    ArtifactExportResponse,
    ConnectorTestResponse,
    PlatformOverviewResponse,
    PolicyExportRequest,
    WorkflowExportRequest,
)
from app.core.state import DatasetRecord, store
from app.services.ingestion import _clean_dataframe
from app.services.policy_engine import evaluate_policy
from app.services.workflow_builder import build_workflow


def _preview_dataframe(dataframe: pd.DataFrame) -> list[dict]:
    preview = dataframe.head(get_settings().max_preview_rows).copy()
    preview = preview.astype(object).where(pd.notnull(preview), None)
    return preview.to_dict(orient="records")


def _load_connector_dataframe(connector_id: str) -> tuple[pd.DataFrame, str]:
    connector = store.get_connector_record(connector_id)
    if connector.connector_type == "csv_url":
        url = connector.config.get("url")
        if not url:
            raise ValueError("Connector URL is missing.")
        dataframe = pd.read_csv(url)
        filename = connector.name or Path(str(url)).name or "connector.csv"
        return _clean_dataframe(dataframe), filename

    if connector.connector_type == "sqlite":
        path = connector.config.get("path")
        table = connector.config.get("table")
        if not path or not table:
            raise ValueError("SQLite connectors require path and table.")
        connection = sqlite3.connect(path)
        try:
            dataframe = pd.read_sql_query(f"SELECT * FROM {table}", connection)
        finally:
            connection.close()
        filename = f"{Path(path).stem}_{table}.csv"
        return _clean_dataframe(dataframe), filename

    raise ValueError("Unsupported connector type.")


def test_connector(connector_id: str) -> ConnectorTestResponse:
    try:
        dataframe, _filename = _load_connector_dataframe(connector_id)
        return ConnectorTestResponse(
            connector_id=connector_id,
            status="ok",
            detail="Connector reachable and dataset preview generated.",
            row_count=int(dataframe.shape[0]),
            columns=dataframe.columns.tolist(),
            preview=_preview_dataframe(dataframe),
        )
    except Exception as exc:
        return ConnectorTestResponse(
            connector_id=connector_id,
            status="error",
            detail=str(exc),
            row_count=0,
            columns=[],
            preview=[],
        )


def import_from_connector(connector_id: str):
    dataframe, filename = _load_connector_dataframe(connector_id)
    dataset_id = str(uuid4())
    record = DatasetRecord(
        dataset_id=dataset_id,
        filename=filename,
        dataframe=dataframe,
        metadata={"connector_id": connector_id},
    )
    store.save_dataset(record)
    preview = _preview_dataframe(dataframe)
    from app.core.schemas import UploadResponse

    return UploadResponse(
        dataset_id=dataset_id,
        filename=filename,
        rows=int(dataframe.shape[0]),
        columns=int(dataframe.shape[1]),
        preview=preview,
    )


def export_workflow_artifact(request: WorkflowExportRequest) -> ArtifactExportResponse:
    workflow = build_workflow(request.dataset_id, request.goal, request.language, request.model_id)
    summary = workflow.steps[0].rationale if workflow.steps else workflow.goal
    artifact = store.create_export_artifact(
        artifact_type="workflow",
        name=f"workflow-{request.goal}",
        summary=summary,
        content=workflow.model_dump(),
        project_id=request.project_id,
        created_by=request.created_by,
    )
    return ArtifactExportResponse(artifact=artifact.to_schema(), content=workflow.model_dump())


def export_policy_artifact(request: PolicyExportRequest) -> ArtifactExportResponse:
    policy = evaluate_policy(request.dataset_id, request.model_id, request.language)
    artifact = store.create_export_artifact(
        artifact_type="policy",
        name="policy-guardrails",
        summary=policy.recommended_action,
        content=policy.model_dump(),
        project_id=request.project_id,
        created_by=request.created_by,
    )
    return ArtifactExportResponse(artifact=artifact.to_schema(), content=policy.model_dump())


def build_platform_overview() -> PlatformOverviewResponse:
    return PlatformOverviewResponse(
        users=store.list_users(),
        projects=store.list_projects(),
        connectors=store.list_connectors(),
        approvals=store.list_approvals(),
        exports=store.list_exports(),
    )
