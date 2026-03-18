from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_sample_upload_and_profile_flow() -> None:
    upload_response = client.post("/upload/sample")
    assert upload_response.status_code == 200
    dataset = upload_response.json()
    assert dataset["rows"] > 0

    profile_response = client.post("/profile", json={"dataset_id": dataset["dataset_id"]})
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert "target_candidates" in profile
    assert profile["shape"]["columns"] >= 5


def test_end_to_end_train_simulate_summary() -> None:
    upload_response = client.post("/upload/sample")
    dataset = upload_response.json()

    training_response = client.post(
        "/train",
        json={"dataset_id": dataset["dataset_id"], "target": "revenue"},
    )
    assert training_response.status_code == 200
    training = training_response.json()
    assert training["task_type"] == "regression"

    simulate_response = client.post(
        "/simulate",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "changes": {"price": 125, "marketing_spend": 7200},
        },
    )
    assert simulate_response.status_code == 200
    simulation = simulate_response.json()
    assert "narrative" in simulation

    profile = client.post("/profile", json={"dataset_id": dataset["dataset_id"]}).json()
    investigation = client.post("/investigate", json={"dataset_id": dataset["dataset_id"]}).json()
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
    assert summary["recommendations"]


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
