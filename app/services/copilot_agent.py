from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.core.schemas import (
    CopilotAskResponse,
    CopilotPlanStep,
    CopilotSessionState,
    CopilotToolCall,
    MissingDataRecommendation,
)
from app.core.state import store
from app.services.action_engine import recommend_actions
from app.services.enrichment_agent import suggest_enrichment
from app.services.insights import investigate_dataset
from app.services.llm_engine import narrate_copilot_answer
from app.services.ml_engine import train_model
from app.services.root_cause import explain_root_cause
from app.services.scenario_engine import simulate_scenario

INTENT_CONFIDENCE_SCORE = {
    "high": 84,
    "medium": 66,
    "low": 43,
}


def _resolve_follow_up_question(question: str, session: Any) -> str:
    lower = question.strip().lower()
    if lower in {"why?", "why", "explain this further"} and session.last_question:
        return f"Explain this further about: {session.last_question}"
    if lower in {"show me evidence", "evidence"} and session.last_summary:
        return f"Show me evidence for: {session.last_summary}"
    if lower in {"what else should i investigate?", "what else should we investigate?", "what next?"}:
        recent = ", ".join(session.latest_investigation_titles[:2]) or "the strongest signals"
        return f"What should we investigate next after reviewing {recent}?"
    if lower in {"simulate another pricing option", "another pricing option"} and session.last_question:
        return f"Run another pricing scenario related to: {session.last_question}"
    return question


def _detect_intent(question: str) -> str:
    lower = question.lower()
    if any(token in lower for token in ["merge", "join", "combine datasets"]):
        return "merge"
    if any(token in lower for token in ["missing data", "additional data", "what data", "data quality", "donnees manqu", "enrich"]):
        return "data_gap"
    if any(token in lower for token in ["segment", "prioritize", "prioriser", "which region", "quel segment"]):
        return "segment_analysis"
    if any(token in lower for token in ["anomaly", "outlier", "anomalie", "exception"]):
        return "anomaly_investigation"
    if any(token in lower for token in ["enrichment", "enrich", "ameliorer cette analyse", "improve this analysis"]):
        return "enrichment"
    if any(token in lower for token in ["prioritize", "focus on", "which segment", "where should we invest", "allocate", "budget", "invest more"]):
        return "prioritization"
    if any(token in lower for token in ["why", "drop", "decline", "cause", "root cause"]):
        return "root_cause"
    if any(token in lower for token in ["increase price", "should we", "what if", "scenario", "simulate"]):
        return "simulation"
    if any(token in lower for token in ["predict", "forecast", "will"]):
        return "prediction"
    return "diagnosis"


def _pick_target(dataset_id: str, explicit_target: Optional[str]) -> str:
    if explicit_target:
        return explicit_target
    record = store.get_dataset(dataset_id)
    if "revenue" in record.dataframe.columns:
        return "revenue"
    numeric = record.dataframe.select_dtypes(include=["number"]).columns.tolist()
    return numeric[0]


def _build_plan(intent: str) -> List[CopilotPlanStep]:
    plans = {
        "diagnosis": [
            CopilotPlanStep(step="1", purpose="Detect the business question type and retrieve the strongest signals", tool_name="intent_router"),
            CopilotPlanStep(step="2", purpose="Run investigation and anomaly review on the current dataset", tool_name="investigate"),
            CopilotPlanStep(step="3", purpose="Recommend the next best analysis path and business actions", tool_name="actions"),
        ],
        "root_cause": [
            CopilotPlanStep(step="1", purpose="Frame the KPI drop or shift as a non-causal root-cause question", tool_name="intent_router"),
            CopilotPlanStep(step="2", purpose="Quantify likely drivers, interactions, and supporting evidence", tool_name="root_cause"),
            CopilotPlanStep(step="3", purpose="Translate the strongest patterns into recommended next moves", tool_name="actions"),
        ],
        "prediction": [
            CopilotPlanStep(step="1", purpose="Select the most relevant prediction target and model path", tool_name="intent_router"),
            CopilotPlanStep(step="2", purpose="Train or reuse a predictive model and review top drivers", tool_name="train"),
            CopilotPlanStep(step="3", purpose="Summarize reliability, trade-offs, and decision implications", tool_name="actions"),
        ],
        "simulation": [
            CopilotPlanStep(step="1", purpose="Translate the business decision into a modeled scenario", tool_name="intent_router"),
            CopilotPlanStep(step="2", purpose="Train or reuse the predictive model needed for simulation", tool_name="train"),
            CopilotPlanStep(step="3", purpose="Compare baseline against the proposed scenario", tool_name="simulate"),
            CopilotPlanStep(step="4", purpose="Recommend actions with guardrails and trade-offs", tool_name="actions"),
        ],
        "prioritization": [
            CopilotPlanStep(step="1", purpose="Identify the prioritization question and the strongest candidate segments", tool_name="intent_router"),
            CopilotPlanStep(step="2", purpose="Combine investigation signals with predictive support where useful", tool_name="investigate"),
            CopilotPlanStep(step="3", purpose="Run a directional scenario to compare focus alternatives", tool_name="simulate"),
            CopilotPlanStep(step="4", purpose="Recommend where to focus next and what to validate", tool_name="actions"),
        ],
        "segment_analysis": [
            CopilotPlanStep(step="1", purpose="Identify which segment dimension best matches the question", tool_name="intent_router"),
            CopilotPlanStep(step="2", purpose="Review segment-level performance, divergence, and opportunity concentration", tool_name="investigate"),
            CopilotPlanStep(step="3", purpose="Translate segment evidence into recommended commercial focus", tool_name="actions"),
        ],
        "anomaly_investigation": [
            CopilotPlanStep(step="1", purpose="Frame the anomaly question and gather unusual record evidence", tool_name="intent_router"),
            CopilotPlanStep(step="2", purpose="Run anomaly-oriented investigation on the most extreme signals", tool_name="investigate"),
            CopilotPlanStep(step="3", purpose="Recommend business follow-up and validation steps", tool_name="actions"),
        ],
        "data_gap": [
            CopilotPlanStep(step="1", purpose="Review the current dataset limits and analysis blind spots", tool_name="intent_router"),
            CopilotPlanStep(step="2", purpose="Suggest missing data that would materially improve the analysis", tool_name="enrichment"),
        ],
        "enrichment": [
            CopilotPlanStep(step="1", purpose="Review the current dataset blind spots against the business question", tool_name="intent_router"),
            CopilotPlanStep(step="2", purpose="Suggest high-value external or internal data to strengthen the recommendation", tool_name="enrichment"),
        ],
        "merge": [
            CopilotPlanStep(step="1", purpose="Review available datasets and identify viable shared keys", tool_name="datasets"),
        ],
    }
    return plans[intent]


def _follow_ups(intent: str) -> List[str]:
    mapping = {
        "diagnosis": ["Why?", "Show me evidence", "What should we investigate next?"],
        "root_cause": ["Show me evidence", "Simulate another pricing option", "What should we investigate next?"],
        "prediction": ["Show me evidence", "Run a scenario", "What additional data would improve this analysis?"],
        "simulation": ["Simulate another pricing option", "Show me evidence", "What should we investigate next?"],
        "prioritization": ["Which segment should we prioritize?", "Run a scenario", "What additional data would improve this analysis?"],
        "segment_analysis": ["Which segment should we prioritize?", "Show me evidence", "Run a scenario"],
        "anomaly_investigation": ["Show me evidence", "What should we investigate next?", "What additional data would improve this analysis?"],
        "data_gap": ["How should we merge that data?", "Run the analysis again", "What should we investigate next?"],
        "enrichment": ["How should we merge that data?", "What should we investigate next?", "Run the analysis again"],
        "merge": ["Which join keys should we trust?", "Run diagnosis after merge", "What additional data would improve this analysis?"],
    }
    return mapping[intent]


def _build_scenario_changes(reference_row: Dict[str, Any], question: str) -> Dict[str, Any]:
    lower = question.lower()
    changes: Dict[str, Any] = {}

    if "price" in reference_row:
        multiplier = 1.1 if "increase price" in lower or "pricing" in lower else 1.03
        changes["price"] = round(float(reference_row["price"]) * multiplier, 2)
    if "marketing_spend" in reference_row:
        multiplier = 1.15 if "invest" in lower or "marketing" in lower else 1.05
        changes["marketing_spend"] = round(float(reference_row["marketing_spend"]) * multiplier, 2)
    if "discount_pct" in reference_row:
        delta = 1.5 if "price" in lower else 0.5
        changes["discount_pct"] = max(0.0, round(float(reference_row["discount_pct"]) - delta, 2))
    return changes


def _build_missing_data_recommendations(dataset_id: str) -> List[MissingDataRecommendation]:
    enrichment = suggest_enrichment(dataset_id)
    recommendations: List[MissingDataRecommendation] = []
    for item in enrichment.suggestions[:4]:
        recommendations.append(
            MissingDataRecommendation(
                dataset_name=item.dataset_name,
                why_it_matters=item.why_it_matters,
                what_it_improves=item.business_question_helped,
                merge_hint=f"{item.integration_hint} Likely join key: {item.likely_join_key}",
            )
        )
    return recommendations


def _update_session(
    session_id: Optional[str],
    dataset_id: str,
    question: str,
    intent: str,
    active_model_id: Optional[str],
    summary: Optional[str],
    simulation_text: Optional[str],
    latest_investigation_titles: List[str],
    latest_recommended_actions: List[str],
) -> CopilotSessionState:
    session = store.get_or_create_session(session_id, dataset_id)
    session.active_dataset_id = dataset_id
    session.active_model_id = active_model_id or session.active_model_id
    session.last_question = question
    session.last_intent = intent
    session.last_summary = summary
    session.last_simulation = simulation_text
    session.latest_investigation_titles = latest_investigation_titles[:5]
    session.latest_recommended_actions = latest_recommended_actions[:5]
    session.message_history = (session.message_history + [question])[-10:]
    return session.to_schema()


def answer_business_question(
    dataset_id: str,
    question: str,
    target: Optional[str] = None,
    model_id: Optional[str] = None,
    session_id: Optional[str] = None,
    language: str = "en",
) -> Tuple[CopilotAskResponse, CopilotSessionState]:
    session = store.get_or_create_session(session_id, dataset_id)
    resolved_question = _resolve_follow_up_question(question, session)
    intent = _detect_intent(resolved_question)
    plan = _build_plan(intent)
    tools_used: List[CopilotToolCall] = []
    supporting_evidence: List[str] = []
    key_drivers: List[str] = []
    short_answer = ""
    confidence_level = "medium"
    simulation_result = None
    recommended_actions: List[str] = []
    suggested_next_investigation: List[str] = []
    data_coverage_pct: Optional[float] = None
    model_reliability: Optional[str] = None
    guardrail = "This analysis is based on statistical patterns and model behavior, not causal inference."

    resolved_model_id = model_id or session.active_model_id
    missing_useful_data = _build_missing_data_recommendations(dataset_id)

    investigation = None
    training = None
    simulation = None

    if intent in {"diagnosis", "prioritization", "segment_analysis", "anomaly_investigation"}:
        investigation = investigate_dataset(dataset_id)
        tools_used.append(
            CopilotToolCall(tool_name="investigate", status="completed", output_summary="Ranked insights, anomalies, and investigation suggestions were generated.")
        )
        key_drivers.extend([item.title for item in investigation.insights[:3]])
        supporting_evidence.extend([item.description for item in investigation.insights[:3]])
        suggested_next_investigation = [item.title for item in investigation.investigation_suggestions[:3]]
        data_coverage_pct = investigation.key_stats.get("data_coverage_pct")

    if intent == "root_cause":
        metric = target or "revenue"
        root_cause = explain_root_cause(dataset_id, metric)
        tools_used.append(
            CopilotToolCall(tool_name="root_cause", status="completed", output_summary=f"Root-cause analysis completed for {metric}.")
        )
        short_answer = root_cause.explanation
        key_drivers.extend([driver.driver for driver in root_cause.main_drivers[:3]])
        supporting_evidence.extend(root_cause.evidence[:4])
        recommended_actions = [f"Investigate {driver.driver} more deeply before acting broadly." for driver in root_cause.main_drivers[:3]]
        suggested_next_investigation = ["Compare recent vs historical periods", "Review segment-level variance", "Run a directional scenario"]

    if intent in {"prediction", "simulation", "prioritization"}:
        if resolved_model_id:
            training_record = store.get_model(resolved_model_id)
            selected_target = training_record.target
        else:
            selected_target = _pick_target(dataset_id, target)
        training = train_model(dataset_id, selected_target)
        tools_used.append(
            CopilotToolCall(tool_name="train", status="completed", output_summary=f"Predictive model prepared for {training.target}.")
        )
        key_drivers.extend(training.top_drivers[:3])
        supporting_evidence.append(
            f"Model {training.model_name} trained with {training.primary_metric_name}={training.primary_metric_value} and {training.data_coverage_pct}% data coverage."
        )
        confidence_level = training.confidence_level
        data_coverage_pct = training.data_coverage_pct
        model_reliability = f"{training.model_name} with {training.primary_metric_name}={training.primary_metric_value}"

    if intent in {"simulation", "prioritization"} and training:
        changes = _build_scenario_changes(training.reference_row, resolved_question)
        if changes:
            simulation = simulate_scenario(dataset_id, training.model_id, changes)
            tools_used.append(
                CopilotToolCall(tool_name="simulate", status="completed", output_summary="Baseline versus alternative scenario comparison executed.")
            )
            simulation_result = simulation.impact_summary
            supporting_evidence.append(simulation.impact_summary)
            confidence_level = simulation.confidence_level
            data_coverage_pct = simulation.data_coverage_pct

    if intent in {"data_gap", "enrichment"}:
        tools_used.append(
            CopilotToolCall(tool_name="enrichment", status="completed", output_summary="Missing useful datasets and merge hints were generated.")
        )
        short_answer = (
            "The current analysis can move forward, but a few additional datasets would make the explanation and recommendations more decision-ready."
            if language == "en"
            else "L'analyse actuelle peut avancer, mais quelques jeux de donnees supplementaires rendraient l'explication et les recommandations plus solides."
        )
        key_drivers.extend([item.dataset_name for item in missing_useful_data[:3]])
        supporting_evidence.extend([item.why_it_matters for item in missing_useful_data[:3]])
        recommended_actions = [
            (f"Add {item.dataset_name} to improve analysis quality." if language == "en" else f"Ajouter {item.dataset_name} pour ameliorer la qualite de l'analyse.")
            for item in missing_useful_data[:3]
        ]
        suggested_next_investigation = (
            ["Review campaign timing", "Compare calendar effects", "Validate segmentation gaps"]
            if language == "en"
            else ["Examiner le calendrier des campagnes", "Comparer les effets calendaires", "Valider les ecarts de segmentation"]
        )

    if intent == "merge":
        tools_used.append(
            CopilotToolCall(tool_name="datasets", status="completed", output_summary="Available datasets were reviewed for merge planning.")
        )
        dataset_labels = [item.filename for item in store.list_datasets()[:3]]
        short_answer = (
            "Multiple datasets are available in session. The next step is to validate shared keys such as date, region, product, or customer identifiers before merging."
            if language == "en"
            else "Plusieurs jeux de donnees sont disponibles dans la session. L'etape suivante consiste a valider des cles partagees comme date, region, produit ou identifiant client avant de fusionner."
        )
        key_drivers.extend(dataset_labels)
        supporting_evidence.append(f"{len(store.list_datasets())} datasets are currently loaded in this session.")
        recommended_actions = ["Open merge preview", "Validate overlap quality", "Re-run the investigation after merging"] if language == "en" else ["Ouvrir l'aperçu de fusion", "Valider la qualite du recouvrement", "Relancer l'investigation apres fusion"]
        suggested_next_investigation = ["Inspect shared keys", "Validate overlap quality", "Re-run insights after merge"] if language == "en" else ["Inspecter les cles partagees", "Valider la qualite du recouvrement", "Relancer les insights apres fusion"]

    if intent in {"diagnosis", "prioritization", "segment_analysis", "anomaly_investigation"}:
        actions = recommend_actions(
            {"insights": [item.model_dump() for item in investigation.insights] if investigation else []},
            training.model_dump() if training else None,
            simulation.model_dump() if simulation else None,
        )
        tools_used.append(
            CopilotToolCall(tool_name="actions", status="completed", output_summary="Business recommendations were generated from the strongest signals.")
        )
        recommended_actions = [item.title for item in actions[:3]]
        if intent == "diagnosis":
            short_answer = investigation.executive_brief if investigation else "The copilot found a small set of ranked signals worth investigating next."
        elif intent == "segment_analysis":
            short_answer = (
                "The strongest evidence suggests concentrating attention on the segments with higher modeled upside and more resilient performance."
                if language == "en"
                else "Les signaux les plus solides suggerent de concentrer l'attention sur les segments au potentiel modele plus eleve et a la performance plus resiliente."
            )
        elif intent == "anomaly_investigation":
            short_answer = (
                "A small set of unusual records appears to be contributing disproportionately to the current performance story."
                if language == "en"
                else "Un petit ensemble d'observations inhabituelles semble contribuer de maniere disproportionnee a la performance actuelle."
            )
        else:
            short_answer = "The strongest current evidence suggests prioritizing the segments and levers that already show stronger modeled performance and lower downside risk."
            if simulation_result:
                short_answer += f" The scenario view indicates: {simulation_result}"

    if intent == "prediction" and training:
        recommended_actions = [
            "Validate the top modeled driver with business stakeholders.",
            "Run a scenario before broad rollout.",
            "Use the model to prioritize the next business review.",
        ]
        short_answer = f"The predictive model suggests that {training.target} is mainly associated with {', '.join(training.top_drivers[:3])}."
        suggested_next_investigation = ["Explain top features", "Run a scenario", "Check data gaps"]

    if intent == "simulation" and simulation:
        recommended_actions = [
            "Test the strongest scenario in a controlled business environment.",
            "Review the most sensitive model drivers before rollout.",
            "Monitor segment-specific response after any change.",
        ]
        short_answer = f"The modeled scenario indicates: {simulation.impact_summary}"
        suggested_next_investigation = ["Try another pricing option", "Inspect root cause", "Review segment sensitivity"]

    if not key_drivers and investigation:
        key_drivers = [item.title for item in investigation.insights[:3]]
    if not supporting_evidence and investigation:
        supporting_evidence = [item.description for item in investigation.insights[:3]]
    if not short_answer:
        short_answer = "The copilot reviewed the available evidence and recommends focusing next on the strongest ranked signals."

    copilot_narrative = narrate_copilot_answer(
        {
            "question": resolved_question,
            "intent": intent,
            "short_answer": short_answer,
            "key_drivers": key_drivers,
            "supporting_evidence": supporting_evidence,
            "confidence_level": confidence_level,
            "recommended_actions": recommended_actions,
            "suggested_next_investigation": suggested_next_investigation,
            "missing_useful_data": [item.model_dump() for item in missing_useful_data],
            "guardrail": guardrail,
            "language": language,
        }
    )
    short_answer = copilot_narrative["short_answer"]
    key_drivers = copilot_narrative["key_drivers"]
    supporting_evidence = copilot_narrative["supporting_evidence"]
    confidence_level = copilot_narrative["confidence_level"]
    recommended_actions = copilot_narrative["recommended_actions"]
    suggested_next_investigation = copilot_narrative["suggested_next_investigation"]

    if isinstance(copilot_narrative.get("missing_useful_data"), list) and copilot_narrative["missing_useful_data"]:
        llm_data = copilot_narrative["missing_useful_data"]
        if isinstance(llm_data[0], dict):
            missing_useful_data = [
                MissingDataRecommendation(
                    dataset_name=item.get("dataset_name", fallback.dataset_name),
                    why_it_matters=item.get("why_it_matters", fallback.why_it_matters),
                    what_it_improves=item.get("what_it_improves", fallback.what_it_improves),
                    merge_hint=item.get("merge_hint", fallback.merge_hint),
                )
                for item, fallback in zip(llm_data[:4], missing_useful_data)
            ]

    latest_titles = suggested_next_investigation[:]
    if investigation:
        latest_titles = [item.title for item in investigation.investigation_suggestions[:5]]

    session_state = _update_session(
        session_id=session_id,
        dataset_id=dataset_id,
        question=resolved_question,
        intent=intent,
        active_model_id=training.model_id if training else resolved_model_id,
        summary=short_answer,
        simulation_text=simulation_result,
        latest_investigation_titles=latest_titles,
        latest_recommended_actions=recommended_actions,
    )

    response = CopilotAskResponse(
        dataset_id=dataset_id,
        session_id=session_state.session_id,
        intent=intent,  # type: ignore[arg-type]
        answer=short_answer,
        short_answer=short_answer,
        plan=plan,
        tools_used=tools_used,
        key_drivers=key_drivers[:4],
        supporting_evidence=supporting_evidence[:5],
        simulation_result=simulation_result,
        confidence_level=confidence_level,  # type: ignore[arg-type]
        confidence_score=INTENT_CONFIDENCE_SCORE.get(confidence_level, 66),
        data_coverage_pct=float(data_coverage_pct) if data_coverage_pct is not None else None,
        model_reliability=model_reliability,
        recommended_actions=recommended_actions[:4],
        suggested_next_investigation=suggested_next_investigation[:5],
        missing_useful_data=missing_useful_data[:4],
        guardrail=guardrail,
        follow_up_questions=_follow_ups(intent),
    )
    return response, session_state
