from __future__ import annotations

from app.core.schemas import ExperimentDesignerResponse, ExperimentRecommendation
from app.core.state import store


def build_experiment_plan(dataset_id: str, model_id: str | None = None, language: str = "en") -> ExperimentDesignerResponse:
    dataset = store.get_dataset(dataset_id)
    model = store.get_model(model_id) if model_id else next((record for record in store.models.values() if record.dataset_id == dataset_id), None)
    target = model.target if model else ("revenue" if "revenue" in dataset.dataframe.columns else dataset.dataframe.columns[-1])
    top_driver = model.top_drivers[0] if model and model.top_drivers else ("price" if "price" in dataset.dataframe.columns else dataset.dataframe.columns[0])
    segment = "customer_segment" if "customer_segment" in dataset.dataframe.columns else "region" if "region" in dataset.dataframe.columns else "all users"

    recommendations = [
        ExperimentRecommendation(
            title="Pricing uplift test" if language == "en" else "Test de hausse tarifaire",
            hypothesis=(
                f"A controlled change on {top_driver} can improve {target} without harming the main guardrail."
                if language == "en"
                else f"Une variation controlee de {top_driver} peut ameliorer {target} sans detruire le garde-fou principal."
            ),
            primary_metric=target,
            guardrail="churn_risk or volume stability" if language == "en" else "churn_risk ou stabilite du volume",
            target_segment=segment,
        ),
        ExperimentRecommendation(
            title="Targeted spend allocation" if language == "en" else "Allocation ciblee du spend",
            hypothesis=(
                "Concentrating spend on the strongest segment should increase modeled return."
                if language == "en"
                else "Concentrer le spend sur le segment le plus fort devrait augmenter le rendement modele."
            ),
            primary_metric=target,
            guardrail="cost efficiency" if language == "en" else "efficience cout",
            target_segment=segment,
        ),
        ExperimentRecommendation(
            title="Offer mix comparison" if language == "en" else "Comparaison de mix offre",
            hypothesis=(
                "Different product or offer mixes may unlock a more robust recommendation."
                if language == "en"
                else "Des mixes produit ou offre differents peuvent debloquer une recommandation plus robuste."
            ),
            primary_metric=target,
            guardrail="segment fairness" if language == "en" else "equilibre entre segments",
            target_segment=segment,
        ),
    ]

    return ExperimentDesignerResponse(
        dataset_id=dataset_id,
        recommendations=recommendations,
        recommended_order=[item.title for item in recommendations],
    )
