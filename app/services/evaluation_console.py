from __future__ import annotations

from collections import Counter

from app.core.schemas import EvaluationConsoleResponse
from app.core.state import store


def build_evaluation_console(language: str = "en") -> EvaluationConsoleResponse:
    logs = store.operation_logs
    total = len(logs)
    if not total:
      readiness = "No activity yet" if language == "en" else "Aucune activite pour le moment"
      return EvaluationConsoleResponse(
          total_operations=0,
          success_rate_pct=0.0,
          fallback_rate_pct=0.0,
          top_routes=[],
          top_tools=[],
          readiness_label=readiness,
      )

    success_count = sum(1 for item in logs if item.status == "completed")
    fallback_count = sum(1 for item in logs if item.status == "fallback")
    route_counts = Counter(item.route for item in logs)
    tool_counts = Counter(item.tool_name for item in logs)
    success_rate = round((success_count / total) * 100, 1)
    fallback_rate = round((fallback_count / total) * 100, 1)

    if success_rate >= 80 and fallback_rate <= 25:
        readiness = "Builder flow looks demo-ready" if language == "en" else "Le flow builder semble pret pour une demo"
    elif success_rate >= 60:
        readiness = "Builder flow is usable but should be monitored" if language == "en" else "Le flow builder est exploitable mais doit etre surveille"
    else:
        readiness = "Builder flow needs stabilization" if language == "en" else "Le flow builder doit etre stabilise"

    return EvaluationConsoleResponse(
        total_operations=total,
        success_rate_pct=success_rate,
        fallback_rate_pct=fallback_rate,
        top_routes=[route for route, _count in route_counts.most_common(4)],
        top_tools=[tool for tool, _count in tool_counts.most_common(4)],
        readiness_label=readiness,
    )
