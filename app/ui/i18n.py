from __future__ import annotations

from typing import Any


TRANSLATIONS: dict[str, dict[str, str]] = {
    "decision_engine.title": {"en": "Decision Engine", "fr": "Moteur de decision"},
    "decision_engine.subtitle": {
        "en": "Compare scenarios, evaluate risk, and recommend the most robust business action.",
        "fr": "Comparez des scenarios, evaluez les risques et obtenez la recommandation metier la plus robuste.",
    },
    "decision_engine.run": {"en": "Run Decision Engine", "fr": "Lancer le moteur de decision"},
    "decision_engine.language": {"en": "Language", "fr": "Langue"},
    "decision_engine.baseline_mode": {"en": "Baseline mode", "fr": "Mode de reference"},
    "decision_engine.reference_row": {"en": "Reference row", "fr": "Ligne de reference"},
    "decision_engine.average_case": {"en": "Average case", "fr": "Cas moyen"},
    "decision_engine.reference_index": {"en": "Reference row index", "fr": "Index de la ligne de reference"},
    "decision_engine.segment_dimension": {"en": "Segment dimension", "fr": "Dimension de segment"},
    "decision_engine.segment_value": {"en": "Segment value", "fr": "Valeur du segment"},
    "decision_engine.recommended": {"en": "Recommended decision", "fr": "Recommandation"},
    "decision_engine.main_risk": {"en": "Main risk", "fr": "Risque principal"},
    "decision_engine.confidence": {"en": "Confidence", "fr": "Confiance"},
    "decision_engine.robustness": {"en": "Robustness", "fr": "Robustesse"},
    "decision_engine.guardrails": {"en": "Guardrails", "fr": "Garde-fous"},
    "decision_engine.next_analysis": {"en": "Next best analysis", "fr": "Prochaine investigation suggeree"},
    "decision_engine.supporting_evidence": {"en": "Supporting evidence", "fr": "Elements de preuve"},
    "decision_engine.missing_data": {"en": "Missing useful data", "fr": "Donnees utiles manquantes"},
    "decision_engine.evidence_pack": {"en": "Evidence Pack", "fr": "Pack de preuves"},
    "decision_engine.actions": {"en": "Recommended actions", "fr": "Actions recommandees"},
    "decision_engine.scenario_comparison": {"en": "Scenario comparison", "fr": "Comparaison de scenarios"},
    "decision_engine.impact_views": {"en": "Decision impact", "fr": "Impact de la decision"},
    "decision_engine.risk_view": {"en": "Risk view", "fr": "Vue des risques"},
    "decision_engine.core_card_caption": {
        "en": "Best scenario with guardrails",
        "fr": "Meilleur scenario avec garde-fous",
    },
    "decision_engine.unavailable_inputs": {"en": "Unavailable inputs", "fr": "Entrees indisponibles"},
    "decision_engine.simulation_basis": {"en": "Simulation basis", "fr": "Base de simulation"},
    "decision_engine.quality": {"en": "Quality indicators", "fr": "Indicateurs de qualite"},
    "decision_engine.what_improves": {"en": "What would improve this recommendation?", "fr": "Qu'est-ce qui ameliorerait encore cette recommandation ?"},
    "decision_engine.level.reference_row": {"en": "Reference row", "fr": "Ligne de reference"},
    "decision_engine.level.dataset_average": {"en": "Dataset average", "fr": "Moyenne du jeu de donnees"},
    "decision_engine.level.segment_level": {"en": "Segment level", "fr": "Niveau segment"},
    "decision_engine.chart.scenario_title": {"en": "Scenario Comparison", "fr": "Comparaison de scenarios"},
    "decision_engine.chart.scenario_subtitle": {
        "en": "Baseline and alternatives are compared side by side.",
        "fr": "La reference et les alternatives sont comparees cote a cote.",
    },
    "decision_engine.chart.impact_title": {"en": "Decision Impact by Level", "fr": "Impact de la decision par niveau"},
    "decision_engine.chart.impact_subtitle": {
        "en": "Compare local, average, and segment-level sensitivity.",
        "fr": "Comparez la sensibilite locale, moyenne et segmentaire.",
    },
    "decision_engine.chart.risk_title": {"en": "Risk and Uncertainty View", "fr": "Vue des risques et de l'incertitude"},
    "decision_engine.chart.risk_subtitle": {
        "en": "Downside exposure is highlighted before rollout.",
        "fr": "L'exposition au risque est mise en avant avant le deploiement.",
    },
    "decision_engine.chart.annotation.winner": {"en": "Recommended option", "fr": "Option recommandee"},
    "decision_engine.chart.annotation.impact": {"en": "Sensitivity differs by level", "fr": "La sensibilite varie selon le niveau"},
    "decision_engine.chart.annotation.risk": {"en": "Highest downside concentration", "fr": "Concentration maximale du risque"},
    "decision_engine.summary.recommend_template": {
        "en": "Recommend {decision} based on the most robust balance of upside, risk, and confidence.",
        "fr": "Recommander {decision} selon le meilleur equilibre entre potentiel, risque et confiance.",
    },
    "decision_engine.insight.stronger_local": {
        "en": "The impact is stronger for this specific case than for the global average, suggesting higher sensitivity in this context.",
        "fr": "L'impact est plus fort sur ce cas specifique que sur la moyenne globale, ce qui suggere une sensibilite plus elevee dans ce contexte.",
    },
}


def t(key: str, lang: str = "en", **kwargs: Any) -> str:
    value = TRANSLATIONS.get(key, {}).get(lang) or TRANSLATIONS.get(key, {}).get("en") or key
    return value.format(**kwargs) if kwargs else value
