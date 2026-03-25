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
PREFERRED_JOIN_KEYS = ["date", "region", "channel", "product", "marketing_spend"]


def _safe_table_name(name: str, taken: set[str]) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip().lower()).strip("_") or "dataset"
    if normalized[0].isdigit():
        normalized = f"t_{normalized}"
    candidate = normalized
    counter = 2
    while candidate in taken:
        candidate = f"{normalized}_{counter}"
        counter += 1
    return candidate


def _build_table_map(dataset_id: str, additional_dataset_ids: list[str] | None = None) -> tuple[dict[str, pd.DataFrame], str]:
    primary = store.get_dataset(dataset_id)
    taken = {TABLE_NAME}
    tables: dict[str, pd.DataFrame] = {TABLE_NAME: primary.dataframe.copy()}
    for extra_id in additional_dataset_ids or []:
        if extra_id == dataset_id:
            continue
        extra = store.get_dataset(extra_id)
        table_name = _safe_table_name(extra.filename.rsplit(".", 1)[0], taken)
        taken.add(table_name)
        tables[table_name] = extra.dataframe.copy()
    return tables, TABLE_NAME


def _schema_summary(tables: dict[str, pd.DataFrame]) -> dict[str, Any]:
    table_summaries = []
    for table_name, df in tables.items():
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
        table_summaries.append(
            {
                "table_name": table_name,
                "row_count": int(df.shape[0]),
                "columns": columns,
            }
        )
    return {"tables": table_summaries}


def _validate_sql(sql: str, allowed_tables: list[str]) -> str:
    normalized = sql.strip().strip(";")
    lowered = normalized.lower()
    allowed_lower = [table.lower() for table in allowed_tables]
    if not lowered.startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")
    forbidden = ["insert ", "update ", "delete ", "drop ", "alter ", "create ", "attach ", "pragma "]
    if any(token in lowered for token in forbidden):
        raise ValueError("Only read-only SQL is allowed.")
    if ";" in normalized:
        raise ValueError("Only a single SQL statement is allowed.")
    if not any(re.search(rf"\b{re.escape(table)}\b", lowered) for table in allowed_lower):
        raise ValueError("SQL must query one of the allowed tables.")
    return normalized


def _with_safe_limit(sql: str) -> str:
    if re.search(r"\blimit\s+\d+\b", sql, flags=re.IGNORECASE):
        return sql
    return f"SELECT * FROM ({sql}) AS query_result LIMIT {MAX_RESULT_ROWS}"


def _fallback_sql(
    question: str,
    tables: dict[str, pd.DataFrame],
    primary_table: str,
    language: str,
) -> tuple[str, str, list[str]]:
    lowered = question.lower()
    primary_df = tables[primary_table]
    numeric_columns = primary_df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = [col for col in primary_df.columns if col not in numeric_columns]

    preferred_metric = "revenue" if "revenue" in numeric_columns else numeric_columns[0] if numeric_columns else primary_df.columns[0]
    preferred_group = "region" if "region" in categorical_columns else categorical_columns[0] if categorical_columns else None

    if len(tables) > 1:
        for table_name, df in tables.items():
            if table_name == primary_table:
                continue
            shared_keys = [key for key in PREFERRED_JOIN_KEYS if key in primary_df.columns and key in df.columns]
            if not shared_keys:
                continue
            if "revenue" in primary_df.columns and "qualified_pipeline" in df.columns and any(
                token in lowered for token in ["pipeline", "marketing", "campaign", "lead", "compare", "versus", "vs"]
            ):
                join_clause = " AND ".join([f"d.{key} = m.{key}" for key in shared_keys])
                sql = (
                    f"SELECT d.region, SUM(d.revenue) AS total_revenue, "
                    f"SUM(m.qualified_pipeline) AS total_qualified_pipeline "
                    f"FROM {primary_table} d "
                    f"JOIN {table_name} m ON {join_clause} "
                    f"GROUP BY d.region ORDER BY total_revenue DESC"
                )
                explanation = (
                    "This fallback joins sales and marketing context on their shared business keys, then compares revenue and qualified pipeline by region."
                    if language == "en"
                    else "Ce fallback joint les donnees ventes et marketing sur leurs cles partagees, puis compare le revenu et le pipeline qualifie par region."
                )
                return sql, explanation, [primary_table, table_name]

    if preferred_group and any(token in lowered for token in ["average", "avg", "moyen", "moyenne", "mean"]):
        sql = (
            f"SELECT {preferred_group}, AVG({preferred_metric}) AS avg_{preferred_metric} "
            f"FROM {primary_table} GROUP BY {preferred_group} ORDER BY avg_{preferred_metric} DESC"
        )
        explanation = (
            f"This fallback groups the data by {preferred_group} and compares average {preferred_metric}."
            if language == "en"
            else f"Ce fallback regroupe les donnees par {preferred_group} et compare la moyenne de {preferred_metric}."
        )
        return sql, explanation, [primary_table]

    if preferred_metric and any(token in lowered for token in ["sum", "total", "totale"]):
        sql = f"SELECT SUM({preferred_metric}) AS total_{preferred_metric} FROM {primary_table}"
        explanation = (
            f"This fallback computes the total {preferred_metric}."
            if language == "en"
            else f"Ce fallback calcule le total de {preferred_metric}."
        )
        return sql, explanation, [primary_table]

    sql = f"SELECT * FROM {primary_table} LIMIT 10"
    explanation = (
        "This fallback shows a sample of the dataset because the question could not be reliably translated into SQL."
        if language == "en"
        else "Ce fallback affiche un echantillon du dataset car la question n a pas pu etre traduite de facon fiable en SQL."
    )
    return sql, explanation, [primary_table]


def _execute_sql(tables: dict[str, pd.DataFrame], sql: str) -> pd.DataFrame:
    connection = sqlite3.connect(":memory:")
    try:
        for table_name, df in tables.items():
            dataset = df.copy()
            for column in dataset.columns:
                if pd.api.types.is_datetime64_any_dtype(dataset[column]):
                    dataset[column] = dataset[column].astype(str)
            dataset.to_sql(table_name, connection, index=False, if_exists="replace")
        return pd.read_sql_query(_with_safe_limit(sql), connection)
    finally:
        connection.close()


def _extract_used_tables(sql: str, allowed_tables: list[str]) -> list[str]:
    lowered = sql.lower()
    return [table for table in allowed_tables if re.search(rf"\b{re.escape(table.lower())}\b", lowered)]


def answer_with_sql(
    dataset_id: str,
    question: str,
    language: str = "en",
    additional_dataset_ids: list[str] | None = None,
) -> QueryResponse:
    tables, primary_table = _build_table_map(dataset_id, additional_dataset_ids)
    schema = _schema_summary(tables)
    warnings: list[str] = []
    allowed_tables = list(tables.keys())

    sql_payload = generate_sql_query(
        {
            "question": question,
            "language": language,
            "schema": schema,
            "table_name": primary_table,
            "allowed_tables": allowed_tables,
        }
    )
    candidate_sql = sql_payload.get("sql", "")
    explanation = sql_payload.get("explanation", "")

    if not candidate_sql:
        candidate_sql, explanation, used_tables = _fallback_sql(question, tables, primary_table, language)
        warnings.append("LLM SQL generation was unavailable; fallback SQL was used.")
    else:
        used_tables = _extract_used_tables(candidate_sql, allowed_tables)

    try:
        validated_sql = _validate_sql(candidate_sql, allowed_tables)
        result = _execute_sql(tables, validated_sql)
        used_tables = _extract_used_tables(validated_sql, allowed_tables) or used_tables
    except Exception:
        validated_sql, explanation, used_tables = _fallback_sql(question, tables, primary_table, language)
        validated_sql = _validate_sql(validated_sql, allowed_tables)
        result = _execute_sql(tables, validated_sql)
        warnings.append("Generated SQL was adjusted to a safe fallback query.")

    result = result.astype(object).where(pd.notnull(result), None)
    preview = result.to_dict(orient="records")
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
        used_tables=used_tables or [primary_table],
        warnings=warnings,
    )
