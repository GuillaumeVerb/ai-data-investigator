from __future__ import annotations

from app.core.schemas import WorkflowBuilderResponse, WorkflowStep
from app.core.state import store


GOAL_LABELS = {
    "diagnosis": {
        "en": "Diagnosis workflow",
        "fr": "Workflow de diagnostic",
    },
    "pricing_decision": {
        "en": "Pricing decision workflow",
        "fr": "Workflow de decision pricing",
    },
    "marketing_optimization": {
        "en": "Marketing optimization workflow",
        "fr": "Workflow d optimisation marketing",
    },
    "segment_prioritization": {
        "en": "Segment prioritization workflow",
        "fr": "Workflow de priorisation de segment",
    },
}


def build_workflow(
    dataset_id: str,
    goal: str = "pricing_decision",
    language: str = "en",
    model_id: str | None = None,
) -> WorkflowBuilderResponse:
    lang = "fr" if language == "fr" else "en"
    _dataset = store.get_dataset(dataset_id)
    model_available = bool(model_id) or any(record.dataset_id == dataset_id for record in store.models.values())

    steps: list[WorkflowStep] = [
        WorkflowStep(
            step_key="prepare",
            title="Prepare the data" if lang == "en" else "Preparer les donnees",
            tool="prep_agent",
            status="recommended",
            rationale=(
                "Clean typing, missing values, and feature opportunities before modeling."
                if lang == "en"
                else "Nettoyer le typage, les valeurs manquantes et les opportunites de features avant de modeliser."
            ),
        ),
        WorkflowStep(
            step_key="semantic",
            title="Build the semantic layer" if lang == "en" else "Construire la couche semantique",
            tool="semantic_layer",
            status="ready",
            rationale=(
                "Define KPI, dimensions, and entities so later steps stay business-aligned."
                if lang == "en"
                else "Definir KPI, dimensions et entites pour garder les etapes suivantes alignees au metier."
            ),
        ),
        WorkflowStep(
            step_key="query",
            title="Interrogate the data" if lang == "en" else "Interroger les donnees",
            tool="sql_agent",
            status="ready",
            rationale=(
                "Use SQL or a routed question to validate the first hypotheses."
                if lang == "en"
                else "Utiliser SQL ou une question routee pour valider les premieres hypotheses."
            ),
        ),
        WorkflowStep(
            step_key="train",
            title="Train the prediction layer" if lang == "en" else "Entrainer la couche predictive",
            tool="train",
            status="ready" if not model_available else "recommended",
            rationale=(
                "A predictive model helps rank drivers and unlock simulation."
                if lang == "en"
                else "Un modele predictif aide a classer les leviers et debloque la simulation."
            ),
        ),
        WorkflowStep(
            step_key="simulate",
            title="Pressure-test a scenario" if lang == "en" else "Tester un scenario",
            tool="simulate",
            status="recommended" if model_available else "blocked",
            rationale=(
                "Simulate the decision before rollout to compare baseline vs alternative."
                if lang == "en"
                else "Simuler la decision avant de deployer pour comparer la reference a une alternative."
            ),
        ),
        WorkflowStep(
            step_key="decide",
            title="Run the decision workflow" if lang == "en" else "Executer le workflow de decision",
            tool="decision_engine",
            status="recommended" if model_available else "blocked",
            rationale=(
                "Use the decision engine when you need a recommendation, a risk view, and a next step."
                if lang == "en"
                else "Utiliser le moteur de decision quand il faut une recommandation, une vue risque et une prochaine action."
            ),
        ),
    ]

    blockers = [
        (
            "Train a model first to unlock simulation and decision comparison."
            if lang == "en"
            else "Entraine d abord un modele pour debloquer la simulation et la comparaison de decision."
        )
    ] if not model_available else []

    automation_potential = (
        "High: the workflow can already chain preparation, SQL validation, prediction, simulation, and decision support."
        if lang == "en"
        else "Eleve : le workflow peut deja enchainer preparation, validation SQL, prediction, simulation et aide a la decision."
    )

    return WorkflowBuilderResponse(
        dataset_id=dataset_id,
        goal=GOAL_LABELS.get(goal, GOAL_LABELS["pricing_decision"])[lang],
        steps=steps,
        blockers=blockers,
        automation_potential=automation_potential,
    )
