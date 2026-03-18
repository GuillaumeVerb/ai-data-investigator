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
    data_coverage_pct: float
    derived_features: List[str]


class InsightItem(AppBaseModel):
    title: str
    description: str
    severity: Literal["high", "medium", "low"]
    confidence: float = Field(ge=0.0, le=1.0)
    impact_level: Literal["high", "medium", "low"]
    confidence_pct: int = Field(ge=0, le=100)
    insight_type: Literal["anomaly", "trend", "correlation"]
    rank_score: float = Field(ge=0.0, le=1.0)
    icon: str = "insight"


class InvestigationSuggestion(AppBaseModel):
    suggestion_id: str
    title: str
    explanation: str
    investigation_type: Literal["trend", "correlation", "segment", "anomaly"]
    priority_score: float = Field(ge=0.0, le=1.0)
    button_label: str = "Investigate"
    payload: Dict[str, Any]


class InvestigationPathRequest(AppBaseModel):
    dataset_id: str
    suggestion_id: str
    payload: Dict[str, Any]


class InvestigationPathResponse(AppBaseModel):
    suggestion_id: str
    title: str
    analysis: str
    business_implication: str
    supporting_stats: Dict[str, Union[float, int, str]]
    chart_spec: Optional[Dict[str, Any]] = None


class RecommendedAction(AppBaseModel):
    title: str
    rationale: str
    expected_effect: str
    priority: Literal["high", "medium", "low"]


class InvestigateRequest(AppBaseModel):
    dataset_id: str


class InvestigateResponse(AppBaseModel):
    dataset_id: str
    insights: List[InsightItem]
    investigation_suggestions: List[InvestigationSuggestion]
    anomalies: List[Dict[str, Any]]
    key_stats: Dict[str, Union[float, int]]
    chart_specs: List[Dict[str, Any]]
    executive_brief: str
    opportunity_areas: List[str]
    anomaly_narrative: str
    recommended_actions: List[RecommendedAction]


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
    top_drivers: List[str]
    baseline_metrics: Dict[str, float]
    primary_metric_name: str
    primary_metric_value: float
    confidence_level: Literal["high", "medium", "low"]
    data_coverage_pct: float
    feature_importance_chart: Dict[str, Any]
    reference_row: Dict[str, Any]


class SimulationRequest(AppBaseModel):
    dataset_id: str
    model_id: str
    changes: Dict[str, Any]
    reference_index: Optional[int] = None
    comparison_changes: Optional[Dict[str, Any]] = None


class SimulationResponse(AppBaseModel):
    prediction_before: Union[float, str]
    prediction_after: Union[float, str]
    delta: Union[float, str]
    delta_pct: Optional[float]
    narrative: str
    impact_summary: str
    guardrail_note: str
    confidence_level: Literal["high", "medium", "low"]
    data_coverage_pct: float
    comparison_prediction_after: Optional[Union[float, str]] = None
    comparison_delta: Optional[Union[float, str]] = None
    comparison_delta_pct: Optional[float] = None
    comparison_summary: Optional[str] = None
    reference_row: Dict[str, Any]
    simulated_row: Dict[str, Any]
    comparison_row: Optional[Dict[str, Any]] = None


class ActionRequest(AppBaseModel):
    dataset_id: str
    investigation: InvestigateResponse
    training: Optional[TrainResponse] = None
    simulation: Optional[SimulationResponse] = None


class ActionResponse(AppBaseModel):
    dataset_id: str
    recommended_actions: List[RecommendedAction]


class SummaryRequest(AppBaseModel):
    dataset_id: str
    profile: ProfileResponse
    investigation: InvestigateResponse
    training: Optional[TrainResponse] = None
    simulation: Optional[SimulationResponse] = None


class SummaryResponse(AppBaseModel):
    dataset_id: str
    headline: str
    executive_summary: str
    recommendations: List[str]
    limitations: List[str]
    key_findings: List[str]
    main_drivers: List[str]
    risks: List[str]
    opportunities: List[str]
