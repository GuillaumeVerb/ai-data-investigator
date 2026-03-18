from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_sample_upload_profile_and_investigation_flow() -> None:
    upload_response = client.post("/upload/sample")
    assert upload_response.status_code == 200
    dataset = upload_response.json()
    assert dataset["rows"] > 0

    profile_response = client.post("/profile", json={"dataset_id": dataset["dataset_id"]})
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["data_coverage_pct"] > 0
    assert "derived_features" in profile

    investigation_response = client.post("/investigate", json={"dataset_id": dataset["dataset_id"]})
    assert investigation_response.status_code == 200
    investigation = investigation_response.json()
    assert investigation["investigation_suggestions"]
    assert investigation["recommended_actions"]
    assert investigation["insights"][0]["insight_type"] in {"anomaly", "trend", "correlation"}


def test_investigation_path_train_simulate_actions_summary_flow() -> None:
    dataset = client.post("/upload/sample").json()
    investigation = client.post("/investigate", json={"dataset_id": dataset["dataset_id"]}).json()

    suggestion = investigation["investigation_suggestions"][0]
    path_response = client.post(
        "/investigate-path",
        json={
            "dataset_id": dataset["dataset_id"],
            "suggestion_id": suggestion["suggestion_id"],
            "payload": {**suggestion["payload"], "investigation_type": suggestion["investigation_type"]},
        },
    )
    assert path_response.status_code == 200
    assert "analysis" in path_response.json()

    training_response = client.post(
        "/train",
        json={"dataset_id": dataset["dataset_id"], "target": "revenue"},
    )
    assert training_response.status_code == 200
    training = training_response.json()
    assert training["task_type"] == "regression"
    assert len(training["top_drivers"]) <= 5
    assert training["feature_importance_chart"]

    simulate_response = client.post(
        "/simulate",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "changes": {"price": 125, "marketing_spend": 7200, "discount_pct": 6},
            "comparison_changes": {"price": 118, "marketing_spend": 7600, "discount_pct": 4},
        },
    )
    assert simulate_response.status_code == 200
    simulation = simulate_response.json()
    assert simulation["confidence_level"] in {"high", "medium", "low"}
    assert simulation["comparison_prediction_after"] is not None

    actions_response = client.post(
        "/actions",
        json={
            "dataset_id": dataset["dataset_id"],
            "investigation": investigation,
            "training": training,
            "simulation": simulation,
        },
    )
    assert actions_response.status_code == 200
    actions = actions_response.json()
    assert actions["recommended_actions"]

    profile = client.post("/profile", json={"dataset_id": dataset["dataset_id"]}).json()
    summary_response = client.post(
        "/summary",
        json={
            "dataset_id": dataset["dataset_id"],
            "profile": profile,
            "investigation": investigation,
            "training": training,
            "simulation": simulation,
        },
    )
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["key_findings"]
    assert summary["opportunities"]
    assert summary["risks"]


def test_csv_upload_endpoint() -> None:
    sample_csv = Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv"
    with sample_csv.open("rb") as handle:
        response = client.post(
            "/upload",
            files={"file": ("sample_sales.csv", handle, "text/csv")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "sample_sales.csv"
