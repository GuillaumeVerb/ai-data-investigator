from __future__ import annotations

from typing import List, Optional

import pandas as pd
from app.core.schemas import RootCauseDriver, RootCauseResponse
from app.core.state import store
from app.services.charts import build_root_cause_driver_chart


def explain_root_cause(dataset_id: str, metric: str, focus: Optional[str] = None, model_id: Optional[str] = None, language: str = "en") -> RootCauseResponse:
    record = store.get_dataset(dataset_id)
    df = record.dataframe.copy()
    lang = "fr" if language == "fr" else "en"
    if metric not in df.columns:
        raise ValueError(f"Metric '{metric}' not found." if lang == "en" else f"La metrique '{metric}' est introuvable.")

    numeric_columns = [col for col in df.select_dtypes(include=["number"]).columns if col != metric]
    categorical_columns = df.select_dtypes(exclude=["number", "datetime", "datetimetz"]).columns.tolist()
    drivers: List[RootCauseDriver] = []
    evidence: List[str] = []

    for column in numeric_columns[:3]:
        corr = float(df[[metric, column]].corr().iloc[0, 1])
        drivers.append(
            RootCauseDriver(
                driver=column,
                impact_estimate=f"{corr * 100:.1f}% directional relationship" if lang == "en" else f"{corr * 100:.1f}% de relation directionnelle",
                explanation=f"{column} shows a measured correlation of {corr:.2f} with {metric}." if lang == "en" else f"{column} montre une correlation mesuree de {corr:.2f} avec {metric}.",
            )
        )
        evidence.append(f"{column} correlation with {metric}: {corr:.2f}" if lang == "en" else f"Correlation de {column} avec {metric} : {corr:.2f}")

    if categorical_columns:
        segment_col = categorical_columns[0]
        grouped = df.groupby(segment_col, dropna=False)[metric].mean().sort_values(ascending=False)
        if len(grouped) >= 2:
            top = grouped.index[0]
            gap = float(grouped.iloc[0] - grouped.iloc[-1])
            drivers.append(
                RootCauseDriver(
                    driver=str(segment_col),
                    impact_estimate=f"{gap:.2f} average gap" if lang == "en" else f"{gap:.2f} d'ecart moyen",
                    explanation=f"{top} is the strongest segment on {metric}, creating a notable segment spread." if lang == "en" else f"{top} est le segment le plus fort sur {metric}, ce qui cree un ecart segmentaire notable.",
                )
            )
            evidence.append(f"{segment_col} top-to-bottom average gap on {metric}: {gap:.2f}" if lang == "en" else f"Ecart moyen haut-bas de {segment_col} sur {metric} : {gap:.2f}")

    if "date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["date"]):
        ordered = df.sort_values("date")
        early = ordered.head(max(3, len(ordered) // 4))[metric].mean()
        late = ordered.tail(max(3, len(ordered) // 4))[metric].mean()
        delta = float(late - early)
        drivers.append(
            RootCauseDriver(
                driver="time trend",
                impact_estimate=f"{delta:.2f} shift" if lang == "en" else f"{delta:.2f} de variation",
                explanation=f"The recent period differs from the earliest observed period by {delta:.2f} on average {metric}." if lang == "en" else f"La periode recente differe de la premiere periode observee de {delta:.2f} en moyenne sur {metric}.",
            )
        )
        evidence.append(f"Recent vs early average {metric} delta: {delta:.2f}" if lang == "en" else f"Delta moyen recent vs debut sur {metric} : {delta:.2f}")

    drivers = drivers[:5]
    explanation = (
        f"The change in {metric} appears to be explained by a mix of numerical drivers, segment differences, and potential time effects visible in the current dataset."
        if lang == "en"
        else f"La variation de {metric} semble s'expliquer par un mix de leviers numeriques, de differences entre segments et d'effets temporels visibles dans le dataset actuel."
    )

    chart_spec = build_root_cause_driver_chart([driver.model_dump() for driver in drivers], metric) if drivers else None

    return RootCauseResponse(
        dataset_id=dataset_id,
        metric=metric,
        explanation=explanation,
        main_drivers=drivers,
        evidence=evidence[:5],
        chart_spec=chart_spec,
    )
