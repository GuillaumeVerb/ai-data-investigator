from __future__ import annotations

from app.core.schemas import PolicyEngineResponse, PolicyRuleResult
from app.core.state import store


def evaluate_policy(dataset_id: str, model_id: str | None = None, language: str = "en") -> PolicyEngineResponse:
    dataset = store.get_dataset(dataset_id)
    model = store.get_model(model_id) if model_id else next((item for item in store.models.values() if item.dataset_id == dataset_id), None)
    columns = set(dataset.dataframe.columns)
    guardrails: list[str] = []
    rule_results: list[PolicyRuleResult] = []
    allowed_moves: list[str] = []
    blocked_moves: list[str] = []

    if "churn_risk" in columns:
        guardrails.append("Do not increase value on segments with elevated churn risk." if language == "en" else "Ne pas augmenter la valeur sur les segments a churn risk eleve.")
        rule_results.append(
            PolicyRuleResult(
                rule_name="Churn guardrail",
                status="warning",
                implication=(
                    "Any aggressive pricing action should be reviewed against churn risk."
                    if language == "en"
                    else "Toute action pricing agressive doit etre revue au regard du churn risk."
                ),
            )
        )
    if "marketing_spend" in columns:
        guardrails.append("Limit incremental spend until efficiency is validated." if language == "en" else "Limiter le spend incremental tant que l efficience n est pas validee.")
        allowed_moves.append("Controlled spend uplift" if language == "en" else "Hausse controlee du spend")
    if "price" in columns:
        allowed_moves.append("Small price test" if language == "en" else "Petit test de prix")
        blocked_moves.append("Large price shock" if language == "en" else "Choc tarifaire important")
    if model and model.confidence_level == "low":
        rule_results.append(
            PolicyRuleResult(
                rule_name="Model confidence",
                status="block",
                implication=(
                    "Avoid full rollout decisions until model confidence improves."
                    if language == "en"
                    else "Eviter les decisions de deploiement complet tant que la confiance modele n augmente pas."
                ),
            )
        )
        blocked_moves.append("Full rollout" if language == "en" else "Deploiement complet")
    else:
        rule_results.append(
            PolicyRuleResult(
                rule_name="Model confidence",
                status="pass",
                implication=(
                    "The current confidence level is acceptable for controlled decisions."
                    if language == "en"
                    else "Le niveau de confiance actuel est acceptable pour des decisions controlees."
                ),
            )
        )

    recommended_action = (
        "Run a controlled rollout under guardrails."
        if language == "en"
        else "Lancer un deploiement controle sous garde-fous."
    )

    return PolicyEngineResponse(
        dataset_id=dataset_id,
        recommended_action=recommended_action,
        guardrails=guardrails,
        rule_results=rule_results,
        allowed_moves=allowed_moves,
        blocked_moves=blocked_moves,
    )
