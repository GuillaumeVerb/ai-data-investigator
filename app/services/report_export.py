from __future__ import annotations

from uuid import uuid4

from app.core.schemas import ReportExportRequest, ReportExportResponse


def export_html_report(payload: ReportExportRequest) -> ReportExportResponse:
    investigation = payload.investigation.model_dump()
    training = payload.training.model_dump() if payload.training else None
    simulation = payload.simulation.model_dump() if payload.simulation else None
    root_cause = payload.root_cause.model_dump() if payload.root_cause else None

    title = "AI Decision Copilot Report"
    report_id = str(uuid4())

    key_findings = "".join(f"<li>{item.title}</li>" for item in payload.investigation.insights[:5])
    recommendations = "".join(f"<li>{item.title}</li>" for item in payload.investigation.recommended_actions[:5])
    top_drivers = "".join(f"<li>{driver}</li>" for driver in (training["top_drivers"][:5] if training else []))
    root_cause_block = ""
    if root_cause:
        root_cause_block = f"""
        <section>
          <h2>Root Cause Analysis</h2>
          <p>{root_cause['explanation']}</p>
          <ul>{''.join(f"<li><strong>{item['driver']}</strong>: {item['impact_estimate']} — {item['explanation']}</li>" for item in root_cause['main_drivers'])}</ul>
        </section>
        """

    simulation_block = ""
    if simulation:
        comparison = simulation.get("comparison_summary") or "No comparison scenario was run."
        simulation_block = f"""
        <section>
          <h2>Scenario Simulation</h2>
          <p><strong>Baseline:</strong> {simulation['prediction_before']}</p>
          <p><strong>Scenario A:</strong> {simulation['prediction_after']} ({simulation['delta_pct']}%)</p>
          <p><strong>Scenario B:</strong> {comparison}</p>
          <p>{simulation['guardrail_note']}</p>
        </section>
        """

    html = f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>{title}</title>
      <style>
        body {{ font-family: Arial, sans-serif; background: #f7f3ec; color: #1f261f; margin: 0; padding: 2rem; }}
        .hero, section {{ background: white; border-radius: 18px; padding: 1.4rem 1.6rem; margin-bottom: 1rem; box-shadow: 0 12px 34px rgba(0,0,0,.06); }}
        h1, h2 {{ color: #163828; }}
        ul {{ padding-left: 1.2rem; }}
        .meta {{ color: #5a655f; font-size: .95rem; }}
      </style>
    </head>
    <body>
      <div class="hero">
        <h1>{title}</h1>
        <p class="meta">Dataset ID: {payload.dataset_id}</p>
        <p>{investigation['executive_brief']}</p>
      </div>
      <section>
        <h2>Dataset Overview</h2>
        <p>Rows: {payload.profile.shape['rows']} | Columns: {payload.profile.shape['columns']} | Coverage: {payload.profile.data_coverage_pct}%</p>
        <p>Derived features: {', '.join(payload.profile.derived_features[:8]) or 'None'}</p>
      </section>
      <section>
        <h2>Ranked Insights</h2>
        <ul>{key_findings}</ul>
      </section>
      <section>
        <h2>Investigation Suggestions</h2>
        <ul>{''.join(f"<li><strong>{item.title}</strong>: {item.explanation}</li>" for item in payload.investigation.investigation_suggestions[:5])}</ul>
      </section>
      <section>
        <h2>Prediction Engine</h2>
        <p>{f"Model: {training['model_name']} ({training['task_type']}) — {training['primary_metric_name']}={training['primary_metric_value']}" if training else "No model run in this session."}</p>
        <ul>{top_drivers}</ul>
      </section>
      {simulation_block}
      {root_cause_block}
      <section>
        <h2>Recommended Actions</h2>
        <ul>{recommendations}</ul>
      </section>
      <section>
        <h2>Executive Summary</h2>
        <p>{payload.investigation.executive_brief}</p>
      </section>
    </body>
    </html>
    """

    return ReportExportResponse(
        report_id=report_id,
        dataset_id=payload.dataset_id,
        format="html",
        title=title,
        html_content=html,
    )
