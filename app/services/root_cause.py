from __future__ import annotations

from typing import List, Optional

import pandas as pd
import plotly.graph_objects as go

from app.core.schemas import RootCauseDriver, RootCauseResponse
from app.core.state import store
from app.services.charts import _json_safe_figure


def explain_root_cause(dataset_id: str, metric: str, focus: Optional[str] = None, model_id: Optional[str] = None) -> RootCauseResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe.copy()
    if metric not in df.columns:
        raise ValueError(f"Metric '{metric}' not found.")

    numeric_columns = [col for col in df.select_dtypes(include=["number"]).columns if col != metric]
    categorical_columns = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns.tolist()
    drivers: List[RootCauseDriver] = []
    evidence: List[str] = []

    for column in numeric_columns[:3]:
        corr = float(df[[metric, column]].corr().iloc[0, 1])
        drivers.append(
            RootCauseDriver(
                driver=column,
                impact_estimate=f"{corr * 100:.1f}% directional relationship",
                explanation=f"{column} shows a measured correlation of {corr:.2f} with {metric}.",
            )
        )
        evidence.append(f"{column} correlation with {metric}: {corr:.2f}")

    if categorical_columns:
        segment_col = categorical_columns[0]
        grouped = df.groupby(segment_col, dropna=False)[metric].mean().sort_values(ascending=False)
        if len(grouped) >= 2:
            top = grouped.index[0]
            gap = float(grouped.iloc[0] - grouped.iloc[-1])
            drivers.append(
                RootCauseDriver(
                    driver=str(segment_col),
                    impact_estimate=f"{gap:.2f} average gap",
                    explanation=f"{top} is the strongest segment on {metric}, creating a notable segment spread.",
                )
            )
            evidence.append(f"{segment_col} top-to-bottom average gap on {metric}: {gap:.2f}")

    if "date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["date"]):
        ordered = df.sort_values("date")
        early = ordered.head(max(3, len(ordered) // 4))[metric].mean()
        late = ordered.tail(max(3, len(ordered) // 4))[metric].mean()
        delta = float(late - early)
        drivers.append(
            RootCauseDriver(
                driver="time trend",
                impact_estimate=f"{delta:.2f} shift",
                explanation=f"The recent period differs from the earliest observed period by {delta:.2f} on average {metric}.",
            )
        )
        evidence.append(f"Recent vs early average {metric} delta: {delta:.2f}")

    drivers = drivers[:5]
    explanation = (
        f"The change in {metric} appears to be explained by a mix of numerical drivers, segment differences, "
        "and potential time effects visible in the current dataset."
    )

    chart_spec = None
    if drivers:
        fig = go.Figure(
            data=[
                go.Bar(
                    x=[driver.driver for driver in drivers],
                    y=list(range(len(drivers), 0, -1)),
                    text=[driver.impact_estimate for driver in drivers],
                    textposition="auto",
                    marker_color="#b44747",
                )
            ]
        )
        fig.update_layout(title=f"Root-cause drivers for {metric}", xaxis_title="driver", yaxis_title="relative weight")
        chart_spec = _json_safe_figure(fig)

    return RootCauseResponse(
        dataset_id=dataset_id,
        metric=metric,
        explanation=explanation,
        main_drivers=drivers,
        evidence=evidence[:5],
        chart_spec=chart_spec,
    )
