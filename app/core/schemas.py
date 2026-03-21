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


class DatasetListItem(AppBaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int


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
    derived_feature_details: List[Dict[str, str]] = []


class EnrichmentSuggestion(AppBaseModel):
    dataset_name: str
    why_it_matters: str
    integration_hint: str
    expected_value: str
    likely_join_key: str = "date"
    business_question_helped: str = "Improves diagnosis and decision confidence."


class EnrichmentRequest(AppBaseModel):
    dataset_id: str


class EnrichmentResponse(AppBaseModel):
    dataset_id: str
    suggestions: List[EnrichmentSuggestion]


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
    expected_impact: str
    investigation_type: Literal["trend", "correlation", "segment", "anomaly"]
    priority_score: float = Field(ge=0.0, le=1.0)
    confidence_pct: int = Field(ge=0, le=100)
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


class RootCauseRequest(AppBaseModel):
    dataset_id: str
    metric: str
    focus: Optional[str] = None
    model_id: Optional[str] = None


class RootCauseDriver(AppBaseModel):
    driver: str
    impact_estimate: str
    explanation: str


class RootCauseResponse(AppBaseModel):
    dataset_id: str
    metric: str
    explanation: str
    main_drivers: List[RootCauseDriver]
    evidence: List[str]
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


class DecisionEngineRequest(AppBaseModel):
    dataset_id: str
    model_id: str
    baseline_mode: Literal["reference_row", "dataset_average"] = "reference_row"
    reference_index: Optional[int] = None
    segment_column: Optional[str] = None
    segment_value: Optional[str] = None
    language: Literal["en", "fr"] = "en"
    scenario_a: Dict[str, Any]
    scenario_b: Optional[Dict[str, Any]] = None


class DecisionInputControl(AppBaseModel):
    key: str
    label: str
    control_type: Literal["slider", "selectbox"]
    available: bool = True
    reason: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default_value: Optional[Any] = None
    options: List[str] = []


class DecisionScenarioRow(AppBaseModel):
    baseline: Dict[str, Any]
    scenario_a: Dict[str, Any]
    scenario_b: Optional[Dict[str, Any]] = None


class DecisionScenarioComparison(AppBaseModel):
    scenario_key: Literal["baseline", "scenario_a", "scenario_b"]
    prediction: Union[float, str]
    delta: Union[float, str]
    delta_pct: Optional[float] = None


class DecisionComparison(AppBaseModel):
    winner: Literal["baseline", "scenario_a", "scenario_b"]
    scenarios: List[DecisionScenarioComparison]


class DecisionConfidence(AppBaseModel):
    level: Literal["high", "medium", "low"]
    model_reliability: str
    data_size: str
    row_coverage_pct: float
    disclaimer: str


class DecisionImpactView(AppBaseModel):
    view_key: Literal["reference_row", "dataset_average", "segment_level"]
    label: str
    baseline_prediction: Union[float, str]
    recommended_prediction: Union[float, str]
    delta: Union[float, str]
    delta_pct: Optional[float] = None
    insight: str


class DecisionEvidencePack(AppBaseModel):
    supporting_metrics: Dict[str, Union[float, int, str]]
    top_variables: List[str]
    chart_references: List[str]
    scenario_assumptions: List[str]
    quality_indicators: List[str]


class DecisionEngineResponse(AppBaseModel):
    baseline_prediction: Union[float, str]
    scenario_a_prediction: Union[float, str]
    scenario_b_prediction: Optional[Union[float, str]] = None
    prediction_before: Union[float, str]
    prediction_after: Union[float, str]
    delta: Union[float, str]
    delta_pct: Optional[float] = None
    comparison: DecisionComparison
    recommended_decision: Literal["baseline", "scenario_a", "scenario_b"]
    main_risk: str
    confidence: DecisionConfidence
    robustness: Literal["high", "medium", "low"]
    guardrails: List[str]
    key_drivers: List[str]
    supporting_evidence: List[str]
    missing_useful_data: List[MissingDataRecommendation]
    next_best_analysis: str
    simulation_basis_used: str
    impact_views: List[DecisionImpactView]
    risk_summary: str
    chart_specs: List[Dict[str, Any]]
    evidence_pack: DecisionEvidencePack
    model_reliability: str
    data_size: str
    disclaimer: str
    available_inputs: List[DecisionInputControl]
    scenario_rows: DecisionScenarioRow
    recommended_actions: List[RecommendedAction]


class ActionRequest(AppBaseModel):
    dataset_id: str
    investigation: InvestigateResponse
    training: Optional[TrainResponse] = None
    simulation: Optional[SimulationResponse] = None


class ActionResponse(AppBaseModel):
    dataset_id: str
    recommended_actions: List[RecommendedAction]


class MergePreviewRequest(AppBaseModel):
    left_dataset_id: str
    right_dataset_id: str
    join_keys: Optional[List[str]] = None


class MergePreviewResponse(AppBaseModel):
    left_dataset_id: str
    right_dataset_id: str
    suggested_join_keys: List[str]
    available_shared_columns: List[str]
    estimated_overlap_rows: int
    left_rows: int
    right_rows: int
    merge_readiness: Literal["high", "medium", "low"]
    explanation: str
    business_value: str
    compatibility_warnings: List[str]
    preview: List[Dict[str, Any]]


class CopilotAskRequest(AppBaseModel):
    dataset_id: str
    question: str
    target: Optional[str] = None
    model_id: Optional[str] = None
    session_id: Optional[str] = None
    language: Literal["en", "fr"] = "en"


class CopilotPlanStep(AppBaseModel):
    step: str
    purpose: str
    tool_name: str


class CopilotToolCall(AppBaseModel):
    tool_name: str
    status: Literal["completed", "skipped"]
    output_summary: str


class CopilotSessionState(AppBaseModel):
    session_id: str
    active_dataset_id: Optional[str] = None
    active_model_id: Optional[str] = None
    last_question: Optional[str] = None
    last_intent: Optional[str] = None
    last_summary: Optional[str] = None
    last_simulation: Optional[str] = None
    latest_investigation_titles: List[str] = []
    latest_recommended_actions: List[str] = []
    message_history: List[str]


class MissingDataRecommendation(AppBaseModel):
    dataset_name: str
    why_it_matters: str
    what_it_improves: str
    merge_hint: str


class CopilotAskResponse(AppBaseModel):
    dataset_id: str
    session_id: str
    intent: Literal["diagnosis", "root_cause", "prediction", "simulation", "prioritization", "segment_analysis", "anomaly_investigation", "data_gap", "enrichment", "merge"]
    answer: str
    short_answer: str
    plan: List[CopilotPlanStep]
    tools_used: List[CopilotToolCall]
    key_drivers: List[str]
    supporting_evidence: List[str]
    simulation_result: Optional[str] = None
    confidence_level: Literal["high", "medium", "low"]
    confidence_score: int = Field(ge=0, le=100)
    data_coverage_pct: Optional[float] = None
    model_reliability: Optional[str] = None
    recommended_actions: List[str]
    suggested_next_investigation: List[str]
    missing_useful_data: List[MissingDataRecommendation]
    guardrail: str
    follow_up_questions: List[str]


class ReportExportRequest(AppBaseModel):
    dataset_id: str
    profile: ProfileResponse
    investigation: InvestigateResponse
    training: Optional[TrainResponse] = None
    simulation: Optional[SimulationResponse] = None
    root_cause: Optional[RootCauseResponse] = None


class ReportExportResponse(AppBaseModel):
    report_id: str
    dataset_id: str
    format: Literal["html"]
    title: str
    html_content: str


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
