from __future__ import annotations

from app.core.schemas import AbTestPlan, AbTestPlannerResponse
from app.core.state import store


def build_ab_test_plan(dataset_id: str, model_id: str | None = None, language: str = "en") -> AbTestPlannerResponse:
    dataset = store.get_dataset(dataset_id)
    model = store.get_model(model_id) if model_id else next((item for item in store.models.values() if item.dataset_id == dataset_id), None)
    target = model.target if model else ("revenue" if "revenue" in dataset.dataframe.columns else dataset.dataframe.columns[-1])
    plans = [
        AbTestPlan(
            title="Price ladder test" if language == "en" else "Test d echelle tarifaire",
            primary_metric=target,
            variants=["baseline", "+3%", "+5%"],
            sample_guidance="Split by region or segment with equal traffic where possible." if language == "en" else "Repartir par region ou segment avec un trafic aussi equilibre que possible.",
            duration_guidance="Run for at least 2 full business cycles." if language == "en" else "Executer au moins 2 cycles business complets.",
            guardrail_metrics=["churn_risk", "units_sold"] if "units_sold" in dataset.dataframe.columns else ["churn_risk"],
        ),
        AbTestPlan(
            title="Spend reallocation test" if language == "en" else "Test de reallocation du spend",
            primary_metric=target,
            variants=["current mix", "high-performing segment boost"],
            sample_guidance="Use matched regions or channels to reduce structural bias." if language == "en" else "Utiliser des regions ou canaux apparies pour reduire les biais structurels.",
            duration_guidance="Monitor weekly and keep a fixed budget envelope." if language == "en" else "Suivre a la semaine avec une enveloppe budgetaire fixe.",
            guardrail_metrics=["marketing_spend", "qualified_pipeline"] if "qualified_pipeline" in dataset.dataframe.columns else ["marketing_spend"],
        ),
    ]
    rollout_advice = (
        "Start with the smallest reversible experiment before any broad rollout."
        if language == "en"
        else "Commencer par l experience la plus petite et reversible avant tout deploiement large."
    )
    return AbTestPlannerResponse(dataset_id=dataset_id, test_plans=plans, rollout_advice=rollout_advice)
