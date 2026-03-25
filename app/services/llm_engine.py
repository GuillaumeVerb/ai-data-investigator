from __future__ import annotations

import json
from typing import Any, Dict, Optional

from openai import OpenAI

from app.core.config import get_settings
from app.core.schemas import SummaryResponse


def _client() -> Optional[OpenAI]:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    return OpenAI(api_key=settings.openai_api_key)


def llm_status() -> Dict[str, Any]:
    settings = get_settings()
    enabled = bool(settings.openai_api_key)
    return {
        "enabled": enabled,
        "provider": "openai" if enabled else "fallback",
        "model": settings.openai_model if enabled else None,
    }


def _extract_text(response: Any) -> str:
    return getattr(response, "output_text", "").strip()


def _extract_json(response: Any) -> Dict[str, Any]:
    text = _extract_text(response)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found.")
    return json.loads(text[start : end + 1])


def _safe_completion(system_prompt: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    client = _client()
    settings = get_settings()
    if client is None:
        return None
    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=(
                f"{system_prompt}\nReturn valid JSON only.\n\n"
                f"Payload:\n{json.dumps(payload, default=str)}"
            ),
        )
        return _extract_json(response)
    except Exception:
        return None


def narrate_investigation(payload: Dict[str, Any]) -> Dict[str, Any]:
    language = payload.get("language", "en")
    insights = payload.get("insights", [])
    anomalies = payload.get("anomalies", [])
    if language == "fr":
        executive_brief = (
            f"L'investigation a fait ressortir {len(insights)} signaux prioritaires et {len(anomalies)} observations atypiques. "
            "Les motifs les plus forts peuvent maintenant etre traduits en actions commerciales concretes."
        )
        opportunity_areas = [
            "Examiner l'evolution du revenu par periode et par mix de segments.",
            "Tester l'elasticite prix avant tout changement tarifaire large.",
            "Verifier les observations atypiques pour separer le risque d'une opportunite ponctuelle.",
        ]
        anomaly_narrative = (
            f"{len(anomalies)} observations ont ete signalees comme atypiques. "
            "Elles doivent etre traitees comme des pistes business, pas comme des incidents confirmes."
        )
    else:
        executive_brief = (
            f"The investigation surfaced {len(insights)} prioritized signals and {len(anomalies)} anomalous records. "
            "The strongest patterns can now be translated into concrete commercial actions."
        )
        opportunity_areas = [
            "Investigate revenue movement by time period and segment mix.",
            "Pressure-test price elasticity before broad pricing changes.",
            "Review outlier records to separate risk from one-off opportunity.",
        ]
        anomaly_narrative = (
            f"{len(anomalies)} records were flagged as atypical. "
            "These should be reviewed as business leads rather than treated as confirmed incidents."
        )
    fallback = {
        "executive_brief": executive_brief,
        "opportunity_areas": opportunity_areas,
        "anomaly_narrative": anomaly_narrative,
    }
    response = _safe_completion(
        (
            "You are an analytics consultant. Return JSON with executive_brief, opportunity_areas, anomaly_narrative. "
            f"Keep it concise and business-oriented. Write in {language}."
        ),
        payload,
    )
    if not response:
        return fallback
    return {
        "executive_brief": response.get("executive_brief", fallback["executive_brief"]),
        "opportunity_areas": response.get("opportunity_areas", fallback["opportunity_areas"])[:3],
        "anomaly_narrative": response.get("anomaly_narrative", fallback["anomaly_narrative"]),
    }


def narrate_simulation(payload: Dict[str, Any]) -> Dict[str, str]:
    before = payload["prediction_before"]
    after = payload["prediction_after"]
    narrative = payload["narrative"]
    impact_summary = f"Baseline prediction moves from {before} to {after} under the modeled scenario."
    guardrail_note = "This is based on model behavior, not causal inference."
    fallback = {
        "narrative": narrative,
        "impact_summary": impact_summary,
        "guardrail_note": guardrail_note,
    }
    response = _safe_completion(
        (
            "You explain business scenarios. Return JSON with narrative, impact_summary, guardrail_note. "
            "Be concise, executive, and non-causal."
        ),
        payload,
    )
    if not response:
        return fallback
    return {
        "narrative": response.get("narrative", fallback["narrative"]),
        "impact_summary": response.get("impact_summary", fallback["impact_summary"]),
        "guardrail_note": response.get("guardrail_note", fallback["guardrail_note"]),
    }


def _fallback_summary(payload: Dict[str, Any]) -> SummaryResponse:
    investigation = payload["investigation"]
    training = payload.get("training")
    simulation = payload.get("simulation")
    actions = investigation.get("recommended_actions", [])
    insights = investigation.get("insights", [])
    language = payload.get("language", "en")

    headline = "AI Data Investigator Executive Summary" if language == "en" else "Synthese executive AI Data Investigator"
    key_findings = [item["title"] for item in insights[:3]] or (["No major findings yet."] if language == "en" else ["Aucun constat majeur pour le moment."])
    main_drivers = training.get("top_drivers", [])[:3] if training else []
    risks = (
        [
            "Anomalies and segment divergence may signal operational friction or data quality issues.",
            "Predictions should not be interpreted as causal proof.",
            "Model confidence depends on the breadth and representativeness of current data.",
        ]
        if language == "en"
        else [
            "Les anomalies et les ecarts entre segments peuvent signaler des frictions operationnelles ou des problemes de qualite de donnees.",
            "Les predictions ne doivent pas etre interpretees comme une preuve causale.",
            "La confiance dans le modele depend de l'etendue et de la representativite des donnees actuelles.",
        ]
    )
    opportunities = investigation.get("opportunity_areas", [])[:3]
    recommendations = [item["title"] for item in actions[:3]] or (
        [
            "Focus commercial attention on the highest-ranked insight.",
            "Validate the strongest scenario with a controlled test.",
            "Review segment differences before applying blanket decisions.",
        ]
        if language == "en"
        else [
            "Concentrer l'attention commerciale sur l'insight le mieux classe.",
            "Valider le scenario le plus fort avec un test controle.",
            "Verifier les differences entre segments avant toute decision generalisee.",
        ]
    )
    limitations = (
        [
            "This MVP uses baseline-ready modeling rather than full model benchmarking.",
            "Outputs reflect available data and may shift with new observations.",
            "Scenario simulation is directional guidance, not causal evidence.",
        ]
        if language == "en"
        else [
            "Ce MVP utilise une modelisation de base plutot qu'un benchmark complet de modeles.",
            "Les sorties refletent les donnees disponibles et peuvent evoluer avec de nouvelles observations.",
            "La simulation de scenario constitue un guidage directionnel, pas une preuve causale.",
        ]
    )
    executive_summary = investigation.get("executive_brief", "")
    if training:
        executive_summary += (
            (
                f" The prediction engine trained a {training['model_name']} {training['task_type']} model with "
                f"{training['primary_metric_name']}={training['primary_metric_value']}."
            )
            if language == "en"
            else (
                f" Le moteur de prediction a entraine un modele {training['model_name']} de type {training['task_type']} avec "
                f"{training['primary_metric_name']}={training['primary_metric_value']}."
            )
        )
    if simulation:
        executive_summary += (
            f" Latest scenario: {simulation.get('impact_summary', simulation['narrative'])}"
            if language == "en"
            else f" Dernier scenario : {simulation.get('impact_summary', simulation['narrative'])}"
        )

    return SummaryResponse(
        dataset_id=payload["dataset_id"],
        headline=headline,
        executive_summary=executive_summary.strip(),
        recommendations=recommendations,
        limitations=limitations,
        key_findings=key_findings,
        main_drivers=main_drivers,
        risks=risks,
        opportunities=opportunities,
    )


def generate_summary(payload: Dict[str, Any]) -> SummaryResponse:
    fallback = _fallback_summary(payload)
    response = _safe_completion(
        (
            "You are a consulting-firm analytics advisor. Return JSON with headline, executive_summary, "
            "recommendations, limitations, key_findings, main_drivers, risks, opportunities. "
            f"Each list should have 3 concise items. Write in {payload.get('language', 'en')}."
        ),
        payload,
    )
    if not response:
        return fallback
    return SummaryResponse(
        dataset_id=payload["dataset_id"],
        headline=response.get("headline", fallback.headline),
        executive_summary=response.get("executive_summary", fallback.executive_summary),
        recommendations=response.get("recommendations", fallback.recommendations)[:3],
        limitations=response.get("limitations", fallback.limitations)[:3],
        key_findings=response.get("key_findings", fallback.key_findings)[:3],
        main_drivers=response.get("main_drivers", fallback.main_drivers)[:3],
        risks=response.get("risks", fallback.risks)[:3],
        opportunities=response.get("opportunities", fallback.opportunities)[:3],
    )


def narrate_copilot_answer(payload: Dict[str, Any]) -> Dict[str, Any]:
    language = payload.get("language", "en")
    fallback = {
        "short_answer": payload["short_answer"],
        "key_drivers": payload.get("key_drivers", [])[:4],
        "supporting_evidence": payload.get("supporting_evidence", [])[:5],
        "confidence_level": payload.get("confidence_level", "medium"),
        "recommended_actions": payload.get("recommended_actions", [])[:4],
        "suggested_next_investigation": payload.get("suggested_next_investigation", [])[:3],
        "missing_useful_data": payload.get("missing_useful_data", [])[:4],
    }
    response = _safe_completion(
        (
            "You are a senior AI business analyst inside an AI Decision Copilot. "
            "Write the final answer for a business stakeholder. "
            "Return JSON with keys: short_answer, key_drivers, supporting_evidence, confidence_level, "
            "recommended_actions, suggested_next_investigation, missing_useful_data. "
            f"Keep the answer short, concrete, business-oriented, and explicitly non-causal. Write in {language}."
        ),
        payload,
    )
    if not response:
        return fallback
    return {
        "short_answer": response.get("short_answer", fallback["short_answer"]),
        "key_drivers": response.get("key_drivers", fallback["key_drivers"])[:4],
        "supporting_evidence": response.get("supporting_evidence", fallback["supporting_evidence"])[:5],
        "confidence_level": response.get("confidence_level", fallback["confidence_level"]),
        "recommended_actions": response.get("recommended_actions", fallback["recommended_actions"])[:4],
        "suggested_next_investigation": response.get(
            "suggested_next_investigation", fallback["suggested_next_investigation"]
        )[:3],
        "missing_useful_data": response.get("missing_useful_data", fallback["missing_useful_data"])[:4],
    }


def generate_sql_query(payload: Dict[str, Any]) -> Dict[str, Any]:
    language = payload.get("language", "en")
    response = _safe_completion(
        (
            "You are an analytics engineer generating SQL for a single SQLite table called dataset. "
            "Return JSON with sql and explanation. "
            "Rules: SELECT only, one statement only, use exact column names from the schema, "
            "never invent columns, and keep queries concise. "
            f"Write explanation in {language}."
        ),
        payload,
    )
    if not response:
        return {"sql": "", "explanation": ""}
    return {
        "sql": str(response.get("sql", "")).strip(),
        "explanation": response.get("explanation", ""),
    }


def summarize_query_result(payload: Dict[str, Any]) -> Dict[str, str]:
    language = payload.get("language", "en")
    fallback = {
        "explanation": (
            f"The query returned {payload.get('row_count', 0)} rows across {len(payload.get('columns', []))} columns."
            if language == "en"
            else f"La requete a retourne {payload.get('row_count', 0)} lignes sur {len(payload.get('columns', []))} colonnes."
        )
    }
    response = _safe_completion(
        (
            "You summarize SQL query results for business users. "
            "Return JSON with explanation only. Keep it short, precise, and business-oriented."
        ),
        payload,
    )
    if not response:
        return fallback
    return {"explanation": response.get("explanation", fallback["explanation"])}


def explain_sql_query(payload: Dict[str, Any]) -> Dict[str, str]:
    language = payload.get("language", "en")
    fallback = {
        "explanation": (
            "This SQL reads the dataset, applies filters or aggregations, and returns only the rows needed to answer the question."
            if language == "en"
            else "Ce SQL lit le dataset, applique les filtres ou agregations utiles, puis retourne uniquement les lignes necessaires pour repondre a la question."
        )
    }
    response = _safe_completion(
        (
            "You explain SQL to business users. "
            "Return JSON with explanation only. "
            "Explain what the SQL is doing, what the result means, and any caution about interpretation. "
            f"Write in {language} and keep it concise."
        ),
        payload,
    )
    if not response:
        return fallback
    return {"explanation": response.get("explanation", fallback["explanation"])}
