from __future__ import annotations

from app.core.schemas import OrchestrationStage, OrchestrationViewResponse
from app.core.state import store


def build_orchestration_view(dataset_id: str | None = None, language: str = "en") -> OrchestrationViewResponse:
    has_dataset = bool(dataset_id and dataset_id in store.datasets)
    has_model = any(record.dataset_id == dataset_id for record in store.models.values()) if dataset_id else False
    logs = [item for item in store.operation_logs if dataset_id is None or item.dataset_id == dataset_id]
    completed_routes = {item.route for item in logs if item.status == "completed"}

    stages = [
        OrchestrationStage(
            stage="Data prep",
            status="completed" if "prep" in completed_routes else "ready" if has_dataset else "blocked",
            owner="prep_agent",
            detail="Cleanup, typing, and features",
        ),
        OrchestrationStage(
            stage="Semantic layer",
            status="completed" if "semantic" in completed_routes else "ready" if has_dataset else "blocked",
            owner="semantic_layer",
            detail="KPI, dimensions, and entities",
        ),
        OrchestrationStage(
            stage="Query & joins",
            status="completed" if {"sql", "join"} & completed_routes else "ready" if has_dataset else "blocked",
            owner="sql_agent + join_assistant",
            detail="Query validation and source linking",
        ),
        OrchestrationStage(
            stage="Model & simulation",
            status="completed" if {"quant", "constraint"} & completed_routes else "ready" if has_model else "blocked",
            owner="train + optimizer stack",
            detail="Prediction, optimization, and constraints",
        ),
        OrchestrationStage(
            stage="Decision ops",
            status="completed" if {"workflow", "experiment"} & completed_routes else "active" if has_model else "blocked",
            owner="workflow_builder + experiment_designer",
            detail="Decision flow and next experiments",
        ),
    ]

    active_agents = sorted({stage.owner for stage in stages if stage.status in {"active", "completed"}})
    summary = (
        "The orchestration view shows which AI Builder layers are ready, active, or still blocked."
        if language == "en"
        else "La vue d orchestration montre quelles couches AI Builder sont pretes, actives ou encore bloquees."
    )
    return OrchestrationViewResponse(dataset_id=dataset_id, stages=stages, active_agents=active_agents, summary=summary)
