from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.schemas import RecommendedAction


def recommend_actions(
    investigation: Dict[str, Any],
    training: Optional[Dict[str, Any]] = None,
    simulation: Optional[Dict[str, Any]] = None,
) -> List[RecommendedAction]:
    actions: List[RecommendedAction] = []
    insights = investigation.get("insights", [])

    if insights:
        top = insights[0]
        actions.append(
            RecommendedAction(
                title="Prioritize the strongest business driver",
                rationale=f"The top-ranked signal is '{top['title']}', which indicates a concentrated lever for action.",
                expected_effect="Sharper commercial focus and faster testing on the most material performance driver.",
                priority="high",
            )
        )

    actions.append(
        RecommendedAction(
            title="Review pricing and discount discipline",
            rationale="Revenue-oriented datasets often show strong elasticity around price and discount interactions.",
            expected_effect="Better margin protection without relying on broad discounting.",
            priority="high",
        )
    )
    actions.append(
        RecommendedAction(
            title="Rebalance marketing allocation toward responsive segments",
            rationale="Modeled performance is usually uneven across regions, channels, or customer groups.",
            expected_effect="Higher return on spend by concentrating budget where modeled response is stronger.",
            priority="medium",
        )
    )

    if simulation and simulation.get("delta_pct") is not None:
        delta_pct = simulation["delta_pct"]
        priority = "high" if abs(delta_pct) >= 5 else "medium"
        actions.append(
            RecommendedAction(
                title="Validate the best scenario with a controlled business test",
                rationale=f"The latest simulation implies a {delta_pct}% change versus baseline.",
                expected_effect="Faster translation from modeled scenario to decision-ready experiment.",
                priority=priority,
            )
        )

    if training and training.get("top_drivers"):
        driver = training["top_drivers"][0]
        actions.append(
            RecommendedAction(
                title="Build a focused operating review on the main model driver",
                rationale=f"The prediction engine identifies '{driver}' as the strongest modeled driver.",
                expected_effect="Improved governance around the variable with the highest modeled influence.",
                priority="medium",
            )
        )

    return actions[:5]
