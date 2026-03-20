from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_profile_investigation_and_enrichment_flow() -> None:
    dataset = client.post("/upload/sample").json()

    profile = client.post("/profile", json={"dataset_id": dataset["dataset_id"]}).json()
    assert profile["data_coverage_pct"] > 0
    assert "derived_features" in profile

    investigation = client.post("/investigate", json={"dataset_id": dataset["dataset_id"]}).json()
    assert investigation["investigation_suggestions"]
    assert investigation["recommended_actions"]

    enrichment = client.post("/enrichment-suggestions", json={"dataset_id": dataset["dataset_id"]}).json()
    assert enrichment["suggestions"]


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
    sample_csv = Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv"
    with sample_csv.open("rb") as handle:
        second_response = client.post(
            "/upload",
            files={"file": ("sample_sales_copy.csv", handle, "text/csv")},
        )
    assert second_response.status_code == 200
    second = second_response.json()

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

    average_response = client.post(
        "/decision-engine",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "baseline_mode": "dataset_average",
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
