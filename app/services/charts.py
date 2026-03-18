from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json


def _json_safe_figure(fig: go.Figure) -> dict:
    return json.loads(json.dumps(fig.to_plotly_json(), cls=PlotlyJSONEncoder))


def build_chart_specs(df: pd.DataFrame) -> list[dict]:
    chart_specs: list[dict] = []
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns.tolist()

    if numeric_columns:
        primary_numeric = numeric_columns[0]
        fig = go.Figure(data=[go.Histogram(x=df[primary_numeric])])
        fig.update_layout(title=f"Distribution of {primary_numeric}", xaxis_title=primary_numeric)
        chart_specs.append(_json_safe_figure(fig))

    if len(numeric_columns) >= 2:
        fig = go.Figure()
        if categorical_columns:
            category = categorical_columns[0]
            for value, segment in df.groupby(category, dropna=False):
                fig.add_trace(
                    go.Scatter(
                        x=segment[numeric_columns[0]],
                        y=segment[numeric_columns[1]],
                        mode="markers",
                        name=str(value),
                    )
                )
        else:
            fig.add_trace(
                go.Scatter(
                    x=df[numeric_columns[0]],
                    y=df[numeric_columns[1]],
                    mode="markers",
                    name="records",
                )
            )
        fig.update_layout(
            title=f"{numeric_columns[0]} vs {numeric_columns[1]}",
            xaxis_title=numeric_columns[0],
            yaxis_title=numeric_columns[1],
        )
        chart_specs.append(_json_safe_figure(fig))

    if categorical_columns and numeric_columns:
        grouped = (
            df.groupby(categorical_columns[0], dropna=False)[numeric_columns[0]]
            .mean()
            .reset_index()
            .sort_values(by=numeric_columns[0], ascending=False)
            .head(10)
        )
        fig = go.Figure(
            data=[
                go.Bar(
                    x=grouped[categorical_columns[0]],
                    y=grouped[numeric_columns[0]],
                )
            ]
        )
        fig.update_layout(
            title=f"Average {numeric_columns[0]} by {categorical_columns[0]}",
            xaxis_title=categorical_columns[0],
            yaxis_title=numeric_columns[0],
        )
        chart_specs.append(_json_safe_figure(fig))

    return chart_specs[:3]
