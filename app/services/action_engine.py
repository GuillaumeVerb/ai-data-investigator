from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.schemas import RecommendedAction


def recommend_actions(
    investigation: Dict[str, Any],
    training: Optional[Dict[str, Any]] = None,
    simulation: Optional[Dict[str, Any]] = None,
    lang: str = "en",
) -> List[RecommendedAction]:
    actions: List[RecommendedAction] = []
    insights = investigation.get("insights", [])
    simulation = simulation or {}
    training = training or {}

    if insights:
        top = insights[0]
        actions.append(
            RecommendedAction(
                title="Prioritize the strongest business driver" if lang == "en" else "Prioriser le levier business le plus fort",
                rationale=(
                    f"The top-ranked signal is '{top['title']}', which indicates a concentrated lever for action."
                    if lang == "en"
                    else f"Le signal le mieux classe est '{top['title']}', ce qui indique un levier d'action concentre."
                ),
                expected_effect=(
                    "Sharper commercial focus and faster testing on the most material performance driver."
                    if lang == "en"
                    else "Un focus commercial plus net et des tests plus rapides sur le levier de performance le plus materiel."
                ),
                priority="high",
            )
        )

    recommended_decision = simulation.get("recommended_decision")
    scenario_a_changes = simulation.get("scenario_a_changes", {}) or {}
    scenario_b_changes = simulation.get("scenario_b_changes", {}) or {}
    winning_changes = scenario_a_changes if recommended_decision == "scenario_a" else scenario_b_changes if recommended_decision == "scenario_b" else {}

    if any(key in winning_changes for key in ["price", "discount", "discount_pct"]):
        actions.append(
            RecommendedAction(
                title="Adjust pricing with discount guardrails" if lang == "en" else "Ajuster le pricing avec des garde-fous sur les remises",
                rationale=(
                    "The winning scenario changes price or discount, so the commercial upside should be balanced against elasticity and margin risk."
                    if lang == "en"
                    else "Le scenario gagnant modifie le prix ou la remise, donc le potentiel commercial doit etre equilibre face au risque d'elasticite et de marge."
                ),
                expected_effect=(
                    "Stronger revenue capture with tighter control over discount leakage."
                    if lang == "en"
                    else "Une meilleure capture de revenu avec un controle plus strict de la fuite de remise."
                ),
                priority="high",
            )
        )
    else:
        actions.append(
            RecommendedAction(
                title="Review pricing and discount discipline" if lang == "en" else "Revoir la discipline prix et remise",
                rationale=(
                    "Revenue-oriented datasets often show strong elasticity around price and discount interactions."
                    if lang == "en"
                    else "Les jeux de donnees orientes revenu montrent souvent une forte elasticite autour des interactions entre prix et remise."
                ),
                expected_effect=(
                    "Better margin protection without relying on broad discounting."
                    if lang == "en"
                    else "Une meilleure protection de marge sans recourir a des remises generalisees."
                ),
                priority="high",
            )
        )

    if "marketing_spend" in winning_changes:
        actions.append(
            RecommendedAction(
                title="Scale marketing only in responsive pockets" if lang == "en" else "N'intensifier le marketing que dans les poches reactives",
                rationale=(
                    "The recommended scenario increases marketing spend, so the next step is to verify where incremental response is strongest."
                    if lang == "en"
                    else "Le scenario recommande augmente les depenses marketing, donc la prochaine etape consiste a verifier ou la reponse incrementale est la plus forte."
                ),
                expected_effect=(
                    "Higher return on spend by avoiding broad budget expansion."
                    if lang == "en"
                    else "Un meilleur retour sur depense en evitant un elargissement global du budget."
                ),
                priority="medium",
            )
        )
    else:
        actions.append(
            RecommendedAction(
                title="Rebalance marketing allocation toward responsive segments" if lang == "en" else "Reallouer le marketing vers les segments reactifs",
                rationale=(
                    "Modeled performance is usually uneven across regions, channels, or customer groups."
                    if lang == "en"
                    else "La performance modelisee est souvent inegale selon les regions, canaux ou groupes clients."
                ),
                expected_effect=(
                    "Higher return on spend by concentrating budget where modeled response is stronger."
                    if lang == "en"
                    else "Un meilleur retour sur depense en concentrant le budget la ou la reponse modelisee est la plus forte."
                ),
                priority="medium",
            )
        )

    if any(key in winning_changes for key in ["region", "product", "product_mix"]):
        actions.append(
            RecommendedAction(
                title="Focus segmentation on the winning mix or region" if lang == "en" else "Concentrer la segmentation sur le mix ou la region gagnante",
                rationale=(
                    "The recommended scenario changes segment allocation, which should be translated into a targeted commercial plan rather than a blanket rollout."
                    if lang == "en"
                    else "Le scenario recommande modifie l'allocation de segment, ce qui doit etre traduit en plan commercial cible plutot qu'en deploiement general."
                ),
                expected_effect=(
                    "Sharper execution in the customer or product pockets most likely to respond."
                    if lang == "en"
                    else "Une execution plus precise sur les poches client ou produit les plus susceptibles de reagir."
                ),
                priority="medium",
            )
        )

    if simulation.get("delta_pct") is not None:
        delta_pct = simulation["delta_pct"]
        priority = "high" if abs(delta_pct) >= 5 else "medium"
        actions.append(
            RecommendedAction(
                title="Validate the best scenario with a controlled business test" if lang == "en" else "Valider le meilleur scenario avec un test controle",
                rationale=(
                    f"The latest simulation implies a {delta_pct}% change versus baseline."
                    if lang == "en"
                    else f"La derniere simulation implique une variation de {delta_pct}% par rapport a la reference."
                ),
                expected_effect=(
                    "Faster translation from modeled scenario to decision-ready experiment."
                    if lang == "en"
                    else "Un passage plus rapide du scenario modele a une experimentation exploitable pour la decision."
                ),
                priority=priority,
            )
        )

    if training.get("top_drivers"):
        driver = training["top_drivers"][0]
        actions.append(
            RecommendedAction(
                title="Build a focused operating review on the main model driver" if lang == "en" else "Construire une revue operationnelle sur le levier principal du modele",
                rationale=(
                    f"The prediction engine identifies '{driver}' as the strongest modeled driver."
                    if lang == "en"
                    else f"Le moteur de prediction identifie '{driver}' comme le levier modele le plus fort."
                ),
                expected_effect=(
                    "Improved governance around the variable with the highest modeled influence."
                    if lang == "en"
                    else "Une meilleure gouvernance autour de la variable ayant l'influence modelisee la plus forte."
                ),
                priority="medium",
            )
        )

    return actions[:5]
