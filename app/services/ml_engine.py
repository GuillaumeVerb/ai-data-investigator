from __future__ import annotations

from uuid import uuid4

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.core.schemas import TrainResponse
from app.core.state import ModelRecord, store


def _infer_task_type(series: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(series) and series.nunique(dropna=True) > 8:
        return "regression"
    return "classification"


def _build_preprocessor(X: pd.DataFrame) -> tuple[ColumnTransformer, list[str], list[str]]:
    numeric_features = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_features = [col for col in X.columns if col not in numeric_features]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )
    return preprocessor, numeric_features, categorical_features


def _extract_importance(pipeline: Pipeline, feature_columns: list[str]) -> list[dict[str, float | str]]:
    model = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps["preprocessor"]

    try:
        transformed_names = preprocessor.get_feature_names_out()
    except Exception:
        transformed_names = feature_columns

    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return []

    pairs = [
        {"feature": str(name), "importance": round(float(value), 4)}
        for name, value in sorted(
            zip(transformed_names, importances), key=lambda item: item[1], reverse=True
        )
    ]
    return pairs[:10]


def train_model(dataset_id: str, target: str) -> TrainResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe.copy()

    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found.")

    y = df[target]
    X = df.drop(columns=[target])
    X = X.astype(object).where(pd.notnull(X), np.nan)

    task_type = _infer_task_type(y)
    preprocessor, _, _ = _build_preprocessor(X)

    if task_type == "regression":
        model = RandomForestRegressor(n_estimators=150, random_state=42)
        baseline = DummyRegressor(strategy="mean")
    else:
        model = RandomForestClassifier(n_estimators=150, random_state=42)
        baseline = DummyClassifier(strategy="most_frequent")

    stratify = y if task_type == "classification" and y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=stratify
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )
    baseline_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", baseline),
        ]
    )

    pipeline.fit(X_train, y_train)
    baseline_pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    baseline_pred = baseline_pipeline.predict(X_test)

    if task_type == "regression":
        metrics = {
            "mae": round(float(mean_absolute_error(y_test, y_pred)), 4),
            "r2": round(float(r2_score(y_test, y_pred)), 4),
        }
        baseline_metrics = {
            "mae": round(float(mean_absolute_error(y_test, baseline_pred)), 4),
            "r2": round(float(r2_score(y_test, baseline_pred)), 4),
        }
    else:
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "f1_weighted": round(float(f1_score(y_test, y_pred, average="weighted")), 4),
        }
        baseline_metrics = {
            "accuracy": round(float(accuracy_score(y_test, baseline_pred)), 4),
            "f1_weighted": round(float(f1_score(y_test, baseline_pred, average="weighted")), 4),
        }

    reference_row = X.iloc[0].astype(object).where(pd.notnull(X.iloc[0]), None).to_dict()
    model_id = str(uuid4())
    store.save_model(
        ModelRecord(
            model_id=model_id,
            dataset_id=dataset_id,
            target=target,
            task_type=task_type,
            pipeline=pipeline,
            feature_columns=X.columns.tolist(),
            reference_row=reference_row,
        )
    )

    model_name = type(model).__name__
    return TrainResponse(
        dataset_id=dataset_id,
        model_id=model_id,
        task_type=task_type,
        target=target,
        model_name=model_name,
        metrics=metrics,
        feature_importance=_extract_importance(pipeline, X.columns.tolist()),
        baseline_metrics=baseline_metrics,
        reference_row=reference_row,
    )
