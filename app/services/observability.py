from __future__ import annotations

from app.core.schemas import ObservabilityResponse
from app.core.state import store


def get_observability_snapshot() -> ObservabilityResponse:
    return ObservabilityResponse(items=store.list_operation_logs())
