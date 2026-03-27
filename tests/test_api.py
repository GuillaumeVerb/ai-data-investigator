from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_frontend_entrypoint_serves_html() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AI Data Investigator" in response.text
    assert 'data-page="decision"' in response.text


def test_frontend_routes_expose_distinct_product_pages() -> None:
    decision = client.get("/decision")
    builder = client.get("/builder")
    governance = client.get("/gouvernance")

    assert decision.status_code == 200
    assert builder.status_code == 200
    assert governance.status_code == 200

    assert 'data-page="decision"' in decision.text
    assert 'data-page="builder"' in builder.text
    assert 'data-page="governance"' in governance.text


def test_health_endpoint_exposes_llm_status() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["llm_enabled"] in {"true", "false"}
    assert body["llm_provider"] in {"openai", "fallback"}
    assert body["llm_model"]


def test_natural_language_query_endpoint_returns_sql_and_rows() -> None:
    dataset = client.post("/upload/sample").json()
    response = client.post(
        "/query",
        json={
            "dataset_id": dataset["dataset_id"],
            "question": "Show average revenue by region",
            "language": "en",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sql"].lower().startswith("select")
    assert body["row_count"] >= 1
    assert body["columns"]
    assert body["used_tables"]
    assert isinstance(body["result_preview"], list)


def test_query_explanation_endpoint_returns_explanation() -> None:
    response = client.post(
        "/query/explain",
        json={
            "question": "Show average revenue by region",
            "sql": "SELECT region, AVG(revenue) AS avg_revenue FROM dataset GROUP BY region",
            "language": "en",
            "columns": ["region", "avg_revenue"],
            "row_count": 4,
            "result_preview": [{"region": "West", "avg_revenue": 1032.4}],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["explanation"]


def test_multi_dataset_query_can_use_joined_context() -> None:
    sales = client.post("/upload/sample").json()
    marketing = client.post("/upload/sample/marketing").json()
    response = client.post(
        "/query",
        json={
            "dataset_id": sales["dataset_id"],
            "question": "Compare revenue and qualified pipeline by region using marketing context",
            "language": "en",
            "additional_dataset_ids": [marketing["dataset_id"]],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "join" in body["sql"].lower()
    assert len(body["used_tables"]) >= 2
    assert body["row_count"] >= 1


def test_join_assistant_and_semantic_layer_endpoints() -> None:
    sales = client.post("/upload/sample").json()
    marketing = client.post("/upload/sample/marketing").json()

    join_response = client.post(
        "/join-assistant",
        json={"dataset_id": sales["dataset_id"], "language": "en"},
    )
    assert join_response.status_code == 200
    join_body = join_response.json()
    assert join_body["candidates"]
    assert any(item["right_dataset_id"] == marketing["dataset_id"] for item in join_body["candidates"])

    semantic_response = client.post(
        "/semantic-layer",
        json={"dataset_id": sales["dataset_id"], "language": "en"},
    )
    assert semantic_response.status_code == 200
    semantic_body = semantic_response.json()
    assert semantic_body["measures"]
    assert semantic_body["recommended_kpis"]


def test_prep_agent_and_workflow_builder_endpoints() -> None:
    dataset = client.post("/upload/sample").json()

    prep_response = client.post(
        "/prep-agent",
        json={"dataset_id": dataset["dataset_id"], "language": "en"},
    )
    assert prep_response.status_code == 200
    prep_body = prep_response.json()
    assert "typed_columns" in prep_body
    assert prep_body["feature_opportunities"]

    workflow_response = client.post(
        "/workflow-builder",
        json={"dataset_id": dataset["dataset_id"], "goal": "pricing_decision", "language": "en"},
    )
    assert workflow_response.status_code == 200
    workflow_body = workflow_response.json()
    assert workflow_body["steps"]
    assert workflow_body["automation_potential"]


def test_quant_optimizer_and_observability_endpoints() -> None:
    dataset = client.post("/upload/sample").json()
    training = client.post("/train", json={"dataset_id": dataset["dataset_id"], "target": "revenue"}).json()

    optimizer_response = client.post(
        "/quant-optimize",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "objective": "maximize_prediction",
            "language": "en",
        },
    )
    assert optimizer_response.status_code == 200
    optimizer_body = optimizer_response.json()
    assert "recommended_changes" in optimizer_body
    assert optimizer_body["tested_scenarios"] >= 1

    observability_response = client.get("/observability")
    assert observability_response.status_code == 200
    observability_body = observability_response.json()
    assert observability_body["items"]
    assert any(item["tool_name"] == "quant_optimizer" for item in observability_body["items"])


def test_constraint_solver_experiment_designer_and_evaluation_console() -> None:
    dataset = client.post("/upload/sample").json()
    training = client.post("/train", json={"dataset_id": dataset["dataset_id"], "target": "revenue"}).json()

    constraint_response = client.post(
        "/constraint-solver",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "objective": "maximize_prediction",
            "language": "en",
        },
    )
    assert constraint_response.status_code == 200
    constraint_body = constraint_response.json()
    assert constraint_body["constraints_applied"]
    assert "recommended_changes" in constraint_body

    experiment_response = client.post(
        "/experiment-designer",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "language": "en",
        },
    )
    assert experiment_response.status_code == 200
    experiment_body = experiment_response.json()
    assert experiment_body["recommendations"]
    assert experiment_body["recommended_order"]

    evaluation_response = client.get("/evaluation-console")
    assert evaluation_response.status_code == 200
    evaluation_body = evaluation_response.json()
    assert evaluation_body["total_operations"] >= 1
    assert evaluation_body["top_tools"]


def test_policy_engine_ab_test_planner_registry_and_orchestration() -> None:
    dataset = client.post("/upload/sample").json()
    training = client.post("/train", json={"dataset_id": dataset["dataset_id"], "target": "revenue"}).json()

    policy_response = client.post(
        "/policy-engine",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "language": "en",
        },
    )
    assert policy_response.status_code == 200
    policy_body = policy_response.json()
    assert policy_body["guardrails"]
    assert policy_body["rule_results"]

    ab_response = client.post(
        "/ab-test-planner",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "language": "en",
        },
    )
    assert ab_response.status_code == 200
    ab_body = ab_response.json()
    assert ab_body["test_plans"]
    assert ab_body["rollout_advice"]

    registry_response = client.post(
        "/semantic-kpi-registry",
        json={
            "dataset_id": dataset["dataset_id"],
            "language": "en",
        },
    )
    assert registry_response.status_code == 200
    registry_body = registry_response.json()
    assert registry_body["kpis"]
    assert registry_body["recommended_default_kpi"]

    orchestration_response = client.post(
        "/orchestration-view",
        json={
            "dataset_id": dataset["dataset_id"],
            "language": "en",
        },
    )
    assert orchestration_response.status_code == 200
    orchestration_body = orchestration_response.json()
    assert orchestration_body["stages"]
    assert orchestration_body["active_agents"]


def test_platform_connectors_exports_and_approvals() -> None:
    user_response = client.post("/platform/users", json={"name": "Demo Builder", "role": "builder"})
    assert user_response.status_code == 200
    user = user_response.json()

    project_response = client.post(
        "/platform/projects",
        json={"name": "Revenue Workspace", "owner_user_id": user["user_id"]},
    )
    assert project_response.status_code == 200
    project = project_response.json()

    sample_path = str((Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv").resolve())
    connector_response = client.post(
        "/platform/connectors",
        json={
            "name": "Sales CSV",
            "connector_type": "csv_url",
            "config": {"url": sample_path},
            "project_id": project["project_id"],
            "created_by": user["user_id"],
        },
    )
    assert connector_response.status_code == 200
    connector = connector_response.json()

    connector_test = client.post("/platform/connectors/test", json={"connector_id": connector["connector_id"]})
    assert connector_test.status_code == 200
    connector_test_body = connector_test.json()
    assert connector_test_body["status"] == "ok"
    assert connector_test_body["row_count"] >= 1

    imported_dataset = client.post("/platform/connectors/import", json={"connector_id": connector["connector_id"]})
    assert imported_dataset.status_code == 200
    dataset = imported_dataset.json()

    train = client.post("/train", json={"dataset_id": dataset["dataset_id"], "target": "revenue"}).json()

    workflow_export = client.post(
        "/platform/exports/workflow",
        json={
            "dataset_id": dataset["dataset_id"],
            "goal": "pricing_decision",
            "language": "en",
            "model_id": train["model_id"],
            "project_id": project["project_id"],
            "created_by": user["user_id"],
        },
    )
    assert workflow_export.status_code == 200
    workflow_body = workflow_export.json()
    assert workflow_body["artifact"]["artifact_type"] == "workflow"

    policy_export = client.post(
        "/platform/exports/policy",
        json={
            "dataset_id": dataset["dataset_id"],
            "language": "en",
            "model_id": train["model_id"],
            "project_id": project["project_id"],
            "created_by": user["user_id"],
        },
    )
    assert policy_export.status_code == 200
    policy_body = policy_export.json()
    assert policy_body["artifact"]["artifact_type"] == "policy"

    approval_response = client.post(
        "/platform/approvals",
        json={
            "title": "Approve pricing workflow",
            "object_type": "workflow",
            "object_id": workflow_body["artifact"]["artifact_id"],
            "summary": "Ready for human review",
            "project_id": project["project_id"],
            "requested_by": user["user_id"],
        },
    )
    assert approval_response.status_code == 200
    approval = approval_response.json()
    assert approval["status"] == "pending"

    approval_decision = client.post(
        f"/platform/approvals/{approval['approval_id']}/decision",
        json={"decision": "approved", "reviewer": user["user_id"]},
    )
    assert approval_decision.status_code == 200
    approval_decision_body = approval_decision.json()
    assert approval_decision_body["status"] == "approved"

    overview_response = client.get("/platform/overview")
    assert overview_response.status_code == 200
    overview = overview_response.json()
    assert overview["users"]
    assert overview["projects"]
    assert overview["connectors"]
    assert overview["exports"]
    assert overview["approvals"]


def test_profile_investigation_and_enrichment_flow() -> None:
    dataset = client.post("/upload/sample").json()

    profile = client.post("/profile", json={"dataset_id": dataset["dataset_id"]}).json()
    assert profile["data_coverage_pct"] > 0
    assert "derived_features" in profile
    assert profile["derived_feature_details"]

    investigation = client.post("/investigate", json={"dataset_id": dataset["dataset_id"]}).json()
    assert investigation["investigation_suggestions"]
    assert investigation["recommended_actions"]
    assert investigation["investigation_suggestions"][0]["confidence_pct"] >= 0

    enrichment = client.post("/enrichment-suggestions", json={"dataset_id": dataset["dataset_id"]}).json()
    assert enrichment["suggestions"]
    assert enrichment["suggestions"][0]["likely_join_key"]


def test_french_localization_flow() -> None:
    dataset = client.post("/upload/sample").json()

    profile = client.post("/profile", json={"dataset_id": dataset["dataset_id"], "language": "fr"}).json()
    assert "lignes" in profile["headline_findings"][0].lower()

    investigation = client.post("/investigate", json={"dataset_id": dataset["dataset_id"], "language": "fr"}).json()
    assert investigation["executive_brief"]
    assert any("revenu" in item["title"].lower() or "anomal" in item["title"].lower() or "region" in item["title"].lower() for item in investigation["investigation_suggestions"])

    enrichment = client.post("/enrichment-suggestions", json={"dataset_id": dataset["dataset_id"], "language": "fr"}).json()
    assert enrichment["suggestions"]
    assert any("donnees" in item["dataset_name"].lower() or "prix" in item["dataset_name"].lower() or "campagnes" in item["dataset_name"].lower() for item in enrichment["suggestions"])


def test_copilot_session_context_and_report_export_flow() -> None:
    dataset = client.post("/upload/sample").json()
    session_id = "test-session-copilot"

    first_answer = client.post(
        "/copilot/ask",
        json={
            "dataset_id": dataset["dataset_id"],
            "question": "Should we increase price?",
            "target": "revenue",
            "session_id": session_id,
        },
    )
    assert first_answer.status_code == 200
    first_payload = first_answer.json()
    assert first_payload["plan"]
    assert first_payload["tools_used"]
    assert first_payload["session_id"] == session_id
    assert "guardrail" in first_payload
    assert "missing_useful_data" in first_payload
    assert "suggested_next_investigation" in first_payload
    assert first_payload["short_answer"]
    assert first_payload["answer"]
    assert first_payload["supporting_evidence"]
    assert isinstance(first_payload["missing_useful_data"][0], dict)

    session_state = client.get(f"/copilot/session/{session_id}")
    assert session_state.status_code == 200
    assert session_state.json()["last_question"] == "Should we increase price?"
    assert session_state.json()["latest_recommended_actions"]

    second_answer = client.post(
        "/copilot/ask",
        json={
            "dataset_id": dataset["dataset_id"],
            "question": "Explain this further",
            "target": "revenue",
            "session_id": session_id,
        },
    )
    assert second_answer.status_code == 200
    second_payload = second_answer.json()
    assert second_payload["supporting_evidence"]
    assert second_payload["guardrail"] == "This analysis is based on statistical patterns and model behavior, not causal inference."

    data_gap_answer = client.post(
        "/copilot/ask",
        json={
            "dataset_id": dataset["dataset_id"],
            "question": "What additional data would improve this analysis?",
            "target": "revenue",
            "session_id": session_id,
        },
    )
    assert data_gap_answer.status_code == 200
    data_gap_payload = data_gap_answer.json()
    assert data_gap_payload["missing_useful_data"]
    assert data_gap_payload["suggested_next_investigation"]
    assert data_gap_payload["missing_useful_data"][0]["merge_hint"]

    profile = client.post("/profile", json={"dataset_id": dataset["dataset_id"]}).json()
    investigation = client.post("/investigate", json={"dataset_id": dataset["dataset_id"]}).json()
    training = client.post("/train", json={"dataset_id": dataset["dataset_id"], "target": "revenue"}).json()
    simulation = client.post(
        "/simulate",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "changes": {"price": 125, "marketing_spend": 7200, "discount_pct": 6},
        },
    ).json()
    root_cause = client.post(
        "/root-cause",
        json={"dataset_id": dataset["dataset_id"], "metric": "revenue"},
    ).json()

    report = client.post(
        "/report/export",
        json={
            "dataset_id": dataset["dataset_id"],
            "profile": profile,
            "investigation": investigation,
            "training": training,
            "simulation": simulation,
            "root_cause": root_cause,
        },
    )
    assert report.status_code == 200
    report_body = report.json()
    assert report_body["format"] == "html"
    assert "<html" in report_body["html_content"].lower()
    assert "Root Cause Analysis" in report_body["html_content"]


def test_multi_dataset_merge_preview_and_csv_upload() -> None:
    first = client.post("/upload/sample").json()
    second_response = client.post("/upload/sample/marketing")
    assert second_response.status_code == 200
    second = second_response.json()
    assert second["filename"] == "sample_marketing.csv"

    datasets = client.get("/datasets")
    assert datasets.status_code == 200
    assert len(datasets.json()) >= 2

    merge_preview = client.post(
        "/merge-preview",
        json={"left_dataset_id": first["dataset_id"], "right_dataset_id": second["dataset_id"]},
    )
    assert merge_preview.status_code == 200
    body = merge_preview.json()
    assert body["suggested_join_keys"]
    assert "business_value" in body
    assert "compatibility_warnings" in body
    assert body["estimated_overlap_rows"] >= 1


def test_decision_engine_reference_and_average_modes() -> None:
    dataset = client.post("/upload/sample").json()
    training = client.post("/train", json={"dataset_id": dataset["dataset_id"], "target": "revenue"}).json()

    reference_response = client.post(
        "/decision-engine",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "baseline_mode": "reference_row",
            "reference_index": 0,
            "segment_column": "region",
            "segment_value": "South",
            "language": "fr",
            "scenario_a": {"price": 125, "marketing_spend": 7200, "discount": 6, "region": "South", "product_mix": "Beta"},
            "scenario_b": {"price": 100, "marketing_spend": 4800, "discount": 4, "region": "North", "product_mix": "Gamma"},
        },
    )
    assert reference_response.status_code == 200
    reference_body = reference_response.json()
    assert reference_body["recommended_decision"] in {"baseline", "scenario_a", "scenario_b"}
    assert reference_body["comparison"]["winner"] in {"baseline", "scenario_a", "scenario_b"}
    assert reference_body["available_inputs"]
    assert reference_body["scenario_rows"]["scenario_a"]["discount_pct"] == 6
    assert reference_body["scenario_rows"]["scenario_a"]["region"] == "South"
    assert reference_body["scenario_rows"]["scenario_a"]["product"] == "Beta"
    assert reference_body["recommended_actions"]
    assert reference_body["confidence"]["disclaimer"]
    assert reference_body["guardrails"]
    assert reference_body["impact_views"]
    assert any(item["view_key"] == "segment_level" for item in reference_body["impact_views"])
    assert reference_body["missing_useful_data"]
    assert reference_body["chart_specs"]
    assert reference_body["evidence_pack"]["chart_references"]
    assert "Cette recommandation" in reference_body["confidence"]["disclaimer"]

    average_response = client.post(
        "/decision-engine",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "baseline_mode": "dataset_average",
            "language": "en",
            "scenario_a": {"price": 130, "marketing_spend": 6500, "discount": 9},
        },
    )
    assert average_response.status_code == 200
    average_body = average_response.json()
    assert average_body["baseline_prediction"] is not None
    assert average_body["scenario_a_prediction"] is not None
    assert average_body["data_size"] in {"small", "medium", "large"}
    assert average_body["model_reliability"] in {"low", "medium", "high"}
    assert average_body["comparison"]["scenarios"][0]["scenario_key"] == "baseline"
    assert average_body["robustness"] in {"high", "medium", "low"}
    assert average_body["supporting_evidence"]
