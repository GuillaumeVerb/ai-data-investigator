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


def test_investigation_path_root_cause_prediction_simulation_actions_summary_and_copilot() -> None:
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

    root_cause = client.post(
        "/root-cause",
        json={"dataset_id": dataset["dataset_id"], "metric": "revenue"},
    )
    assert root_cause.status_code == 200
    assert root_cause.json()["main_drivers"]

    training = client.post(
        "/train",
        json={"dataset_id": dataset["dataset_id"], "target": "revenue"},
    ).json()
    assert training["feature_importance_chart"]

    simulation = client.post(
        "/simulate",
        json={
            "dataset_id": dataset["dataset_id"],
            "model_id": training["model_id"],
            "changes": {"price": 125, "marketing_spend": 7200, "discount_pct": 6},
            "comparison_changes": {"price": 118, "marketing_spend": 7600, "discount_pct": 4},
        },
    ).json()
    assert simulation["comparison_prediction_after"] is not None

    actions = client.post(
        "/actions",
        json={
            "dataset_id": dataset["dataset_id"],
            "investigation": investigation,
            "training": training,
            "simulation": simulation,
        },
    ).json()
    assert actions["recommended_actions"]

    profile = client.post("/profile", json={"dataset_id": dataset["dataset_id"]}).json()
    summary = client.post(
        "/summary",
        json={
            "dataset_id": dataset["dataset_id"],
            "profile": profile,
            "investigation": investigation,
            "training": training,
            "simulation": simulation,
        },
    ).json()
    assert summary["key_findings"]
    assert summary["risks"]

    copilot = client.post(
        "/copilot/ask",
        json={"dataset_id": dataset["dataset_id"], "question": "Should we increase price?", "target": "revenue"},
    ).json()
    assert copilot["answer"]
    assert copilot["recommended_actions"]


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
