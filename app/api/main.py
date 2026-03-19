from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.core.config import get_settings
from app.core.schemas import (
    ActionRequest,
    ActionResponse,
    CopilotAskRequest,
    CopilotAskResponse,
    CopilotSessionState,
    DatasetListItem,
    EnrichmentRequest,
    EnrichmentResponse,
    InvestigationPathRequest,
    InvestigationPathResponse,
    InvestigateRequest,
    InvestigateResponse,
    MergePreviewRequest,
    MergePreviewResponse,
    ProfileRequest,
    ProfileResponse,
    RootCauseRequest,
    RootCauseResponse,
    ReportExportRequest,
    ReportExportResponse,
    SimulationRequest,
    SimulationResponse,
    SummaryRequest,
    SummaryResponse,
    TrainRequest,
    TrainResponse,
    UploadResponse,
)
from app.services.copilot_agent import answer_business_question
from app.services.dataset_merge import preview_merge
from app.services.enrichment_agent import suggest_enrichment
from app.services.action_engine import recommend_actions
from app.services.ingestion import load_sample_dataset, load_upload
from app.services.investigation_agent import investigate_path
from app.services.insights import investigate_dataset
from app.services.llm_engine import generate_summary
from app.services.ml_engine import train_model
from app.services.profiling import build_profile
from app.services.report_export import export_html_report
from app.services.root_cause import explain_root_cause
from app.services.scenario_engine import simulate_scenario
from app.core.state import store


app = FastAPI(title=get_settings().app_name)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/datasets", response_model=list[DatasetListItem])
def list_datasets() -> list[DatasetListItem]:
    return store.list_datasets()


@app.get("/copilot/session/{session_id}", response_model=CopilotSessionState)
def get_copilot_session(session_id: str) -> CopilotSessionState:
    return store.get_or_create_session(session_id).to_schema()


@app.post("/copilot/session/{session_id}/reset", response_model=CopilotSessionState)
def reset_copilot_session(session_id: str) -> CopilotSessionState:
    return store.reset_session(session_id)


@app.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)) -> UploadResponse:
    try:
        return await load_upload(file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/upload/sample", response_model=UploadResponse)
def upload_sample() -> UploadResponse:
    sample_path = Path(__file__).resolve().parents[2] / "data" / "sample_sales.csv"
    return load_sample_dataset(str(sample_path))


@app.post("/profile", response_model=ProfileResponse)
def profile_dataset(request: ProfileRequest) -> ProfileResponse:
    try:
        return build_profile(request.dataset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Dataset not found.") from exc


@app.post("/investigate", response_model=InvestigateResponse)
def investigate(request: InvestigateRequest) -> InvestigateResponse:
    try:
        return investigate_dataset(request.dataset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Dataset not found.") from exc


@app.post("/investigate-path", response_model=InvestigationPathResponse)
def investigate_single_path(request: InvestigationPathRequest) -> InvestigationPathResponse:
    try:
        return investigate_path(request.dataset_id, request.suggestion_id, request.payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Dataset not found.") from exc


@app.post("/root-cause", response_model=RootCauseResponse)
def root_cause(request: RootCauseRequest) -> RootCauseResponse:
    try:
        return explain_root_cause(request.dataset_id, request.metric, request.focus, request.model_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Dataset not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/enrichment-suggestions", response_model=EnrichmentResponse)
def enrichment_suggestions(request: EnrichmentRequest) -> EnrichmentResponse:
    try:
        return suggest_enrichment(request.dataset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Dataset not found.") from exc


@app.post("/merge-preview", response_model=MergePreviewResponse)
def merge_preview(request: MergePreviewRequest) -> MergePreviewResponse:
    try:
        return preview_merge(request.left_dataset_id, request.right_dataset_id, request.join_keys)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Dataset not found.") from exc


@app.post("/train", response_model=TrainResponse)
def train(request: TrainRequest) -> TrainResponse:
    try:
        return train_model(request.dataset_id, request.target)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Dataset not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/simulate", response_model=SimulationResponse)
def simulate(request: SimulationRequest) -> SimulationResponse:
    try:
        return simulate_scenario(
            dataset_id=request.dataset_id,
            model_id=request.model_id,
            changes=request.changes,
            reference_index=request.reference_index,
            comparison_changes=request.comparison_changes,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Dataset or model not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/actions", response_model=ActionResponse)
def actions(request: ActionRequest) -> ActionResponse:
    return ActionResponse(
        dataset_id=request.dataset_id,
        recommended_actions=recommend_actions(
            investigation=request.investigation.model_dump(),
            training=request.training.model_dump() if request.training else None,
            simulation=request.simulation.model_dump() if request.simulation else None,
        ),
    )


@app.post("/summary", response_model=SummaryResponse)
def summary(request: SummaryRequest) -> SummaryResponse:
    return generate_summary(request.model_dump())


@app.post("/copilot/ask", response_model=CopilotAskResponse)
def copilot_ask(request: CopilotAskRequest) -> CopilotAskResponse:
    try:
        response, _session = answer_business_question(
            request.dataset_id,
            request.question,
            request.target,
            request.model_id,
            request.session_id,
        )
        return response
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Dataset or model not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/report/export", response_model=ReportExportResponse)
def report_export(request: ReportExportRequest) -> ReportExportResponse:
    return export_html_report(request)
