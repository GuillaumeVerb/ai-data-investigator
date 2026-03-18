from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class AppBaseModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class UploadResponse(AppBaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    preview: List[Dict[str, Any]]


class ProfileRequest(AppBaseModel):
    dataset_id: str


class ProfileResponse(AppBaseModel):
    dataset_id: str
    shape: Dict[str, int]
    columns: List[str]
    dtypes: Dict[str, str]
    missing_pct: Dict[str, float]
    numeric_columns: List[str]
    categorical_columns: List[str]
    temporal_columns: List[str]
    target_candidates: List[str]
    quality_score: float
    headline_findings: List[str]


class InsightItem(AppBaseModel):
    title: str
    description: str
    severity: Literal["high", "medium", "low"]
    confidence: float = Field(ge=0.0, le=1.0)


class InvestigateRequest(AppBaseModel):
    dataset_id: str


class InvestigateResponse(AppBaseModel):
    dataset_id: str
    insights: List[InsightItem]
    anomalies: List[Dict[str, Any]]
    key_stats: Dict[str, Union[float, int]]
    chart_specs: List[Dict[str, Any]]


class TrainRequest(AppBaseModel):
    dataset_id: str
    target: str


class TrainResponse(AppBaseModel):
    dataset_id: str
    model_id: str
    task_type: Literal["regression", "classification"]
    target: str
    model_name: str
    metrics: Dict[str, float]
    feature_importance: List[Dict[str, Union[float, str]]]
    baseline_metrics: Dict[str, float]
    reference_row: Dict[str, Any]


class SimulationRequest(AppBaseModel):
    dataset_id: str
    model_id: str
    changes: Dict[str, Any]
    reference_index: Optional[int] = None


class SimulationResponse(AppBaseModel):
    prediction_before: Union[float, str]
    prediction_after: Union[float, str]
    delta: Union[float, str]
    delta_pct: Optional[float]
    narrative: str
    reference_row: Dict[str, Any]
    simulated_row: Dict[str, Any]


class SummaryRequest(AppBaseModel):
    dataset_id: str
    profile: ProfileResponse
    investigation: InvestigateResponse
    training: Optional[TrainResponse] = None
    simulation: Optional[SimulationResponse] = None


class SummaryResponse(AppBaseModel):
    dataset_id: str
    executive_summary: str
    recommendations: List[str]
    limitations: List[str]
