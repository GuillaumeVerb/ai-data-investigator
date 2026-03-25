from __future__ import annotations

import re
import sqlite3
from typing import Any

import pandas as pd

from app.core.schemas import QueryResponse
from app.core.state import store
from app.services.llm_engine import generate_sql_query, summarize_query_result

TABLE_NAME = "dataset"
MAX_RESULT_ROWS = 200


def _schema_summary(df: pd.DataFrame) -> dict[str, Any]:
    columns = []
    for column in df.columns:
        series = df[column]
        sample_values = (
            series.dropna().astype(str).unique().tolist()[:5]
            if series.nunique(dropna=True) <= 12
            else []
        )
        columns.append(
            {
                "name": column,
                "dtype": str(series.dtype),
                "sample_values": sample_values,
            }
        )
    return {"table_name": TABLE_NAME, "row_count": int(df.shape[0]), "columns": columns}


def _validate_sql(sql: str) -> str:
    normalized = sql.strip().strip(";")
    lowered = normalized.lower()
    if not lowered.startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")
    forbidden = ["insert ", "update ", "delete ", "drop ", "alter ", "create ", "attach ", "pragma "]
    if any(token in lowered for token in forbidden):
        raise ValueError("Only read-only SQL is allowed.")
    if TABLE_NAME not in lowered:
        raise ValueError(f"SQL must query the `{TABLE_NAME}` table.")
    if ";" in normalized:
        raise ValueError("Only a single SQL statement is allowed.")
    return normalized


def _with_safe_limit(sql: str) -> str:
    if re.search(r"\blimit\s+\d+\b", sql, flags=re.IGNORECASE):
        return sql
    return f"SELECT * FROM ({sql}) AS query_result LIMIT {MAX_RESULT_ROWS}"


def _fallback_sql(question: str, df: pd.DataFrame, language: str) -> tuple[str, str]:
    lowered = question.lower()
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = [col for col in df.columns if col not in numeric_columns]

    preferred_metric = "revenue" if "revenue" in numeric_columns else numeric_columns[0] if numeric_columns else df.columns[0]
    preferred_group = "region" if "region" in categorical_columns else categorical_columns[0] if categorical_columns else None

    if preferred_group and any(token in lowered for token in ["average", "avg", "moyen", "moyenne", "mean"]):
        sql = (
            f"SELECT {preferred_group}, AVG({preferred_metric}) AS avg_{preferred_metric} "
            f"FROM {TABLE_NAME} GROUP BY {preferred_group} ORDER BY avg_{preferred_metric} DESC"
        )
        explanation = (
            f"This fallback groups the data by {preferred_group} and compares average {preferred_metric}."
            if language == "en"
            else f"Ce fallback regroupe les donnees par {preferred_group} et compare la moyenne de {preferred_metric}."
        )
        return sql, explanation

    if preferred_metric and any(token in lowered for token in ["sum", "total", "totale"]):
        sql = f"SELECT SUM({preferred_metric}) AS total_{preferred_metric} FROM {TABLE_NAME}"
        explanation = (
            f"This fallback computes the total {preferred_metric}."
            if language == "en"
            else f"Ce fallback calcule le total de {preferred_metric}."
        )
        return sql, explanation

    sql = f"SELECT * FROM {TABLE_NAME} LIMIT 10"
    explanation = (
        "This fallback shows a sample of the dataset because the question could not be reliably translated into SQL."
        if language == "en"
        else "Ce fallback affiche un echantillon du dataset car la question n a pas pu etre traduite de facon fiable en SQL."
    )
    return sql, explanation


def _execute_sql(df: pd.DataFrame, sql: str) -> pd.DataFrame:
    connection = sqlite3.connect(":memory:")
    try:
        dataset = df.copy()
        for column in dataset.columns:
            if pd.api.types.is_datetime64_any_dtype(dataset[column]):
                dataset[column] = dataset[column].astype(str)
        dataset.to_sql(TABLE_NAME, connection, index=False, if_exists="replace")
        return pd.read_sql_query(_with_safe_limit(sql), connection)
    finally:
        connection.close()


def answer_with_sql(dataset_id: str, question: str, language: str = "en") -> QueryResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe.copy()
    schema = _schema_summary(df)
    warnings: list[str] = []

    sql_payload = generate_sql_query(
        {
            "question": question,
            "language": language,
            "schema": schema,
            "table_name": TABLE_NAME,
        }
    )
    candidate_sql = sql_payload.get("sql", "")
    explanation = sql_payload.get("explanation", "")

    if not candidate_sql:
        candidate_sql, explanation = _fallback_sql(question, df, language)
        warnings.append("LLM SQL generation was unavailable; fallback SQL was used.")

    try:
        validated_sql = _validate_sql(candidate_sql)
        result = _execute_sql(df, validated_sql)
    except Exception:
        validated_sql, explanation = _fallback_sql(question, df, language)
        validated_sql = _validate_sql(validated_sql)
        result = _execute_sql(df, validated_sql)
        warnings.append("Generated SQL was adjusted to a safe fallback query.")

    result = result.astype(object).where(pd.notnull(result), None)
    preview = result.head(50).to_dict(orient="records")
    summary = summarize_query_result(
        {
            "language": language,
            "question": question,
            "sql": validated_sql,
            "row_count": int(result.shape[0]),
            "columns": result.columns.tolist(),
            "preview": preview[:8],
        }
    )

    return QueryResponse(
        dataset_id=dataset_id,
        question=question,
        sql=validated_sql,
        explanation=summary.get("explanation", explanation),
        result_preview=preview,
        columns=result.columns.tolist(),
        row_count=int(result.shape[0]),
        warnings=warnings,
    )
