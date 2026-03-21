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
from app.services.charts import build_feature_importance_chart
from app.services.feature_engineering import build_derived_features


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

    enriched_df, derived_features, derived_feature_details = build_derived_features(df)
    y = enriched_df[target]
    X = enriched_df.drop(columns=[target])
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
    feature_importance = _extract_importance(pipeline, X.columns.tolist())
    primary_metric_name = "r2" if task_type == "regression" else "accuracy"
    primary_metric_value = metrics[primary_metric_name]
    confidence_level = "high" if primary_metric_value >= 0.75 else "medium" if primary_metric_value >= 0.5 else "low"
    data_coverage_pct = round(float(100 - enriched_df.isna().mean().mean() * 100), 1)
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
            metrics=metrics,
            primary_metric_name=primary_metric_name,
            primary_metric_value=round(float(primary_metric_value), 4),
            confidence_level=confidence_level,
            data_coverage_pct=data_coverage_pct,
            top_drivers=[str(item["feature"]) for item in feature_importance[:5]],
        )
    )
    record.metadata["derived_features"] = derived_features
    record.metadata["derived_feature_details"] = derived_feature_details

    model_name = type(model).__name__
    return TrainResponse(
        dataset_id=dataset_id,
        model_id=model_id,
        task_type=task_type,
        target=target,
        model_name=model_name,
        metrics=metrics,
        feature_importance=feature_importance,
        top_drivers=[str(item["feature"]) for item in feature_importance[:5]],
        baseline_metrics=baseline_metrics,
        primary_metric_name=primary_metric_name,
        primary_metric_value=round(float(primary_metric_value), 4),
        confidence_level=confidence_level,
        data_coverage_pct=data_coverage_pct,
        feature_importance_chart=build_feature_importance_chart(feature_importance),
        reference_row=reference_row,
    )
