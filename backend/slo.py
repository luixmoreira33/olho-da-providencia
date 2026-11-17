"""SLO model foundation (v1.1)."""
from typing import Optional
from pydantic import BaseModel


class SLO(BaseModel):
    app_name: str
    availability_target: float = 99.9
    latency_p95_ms: Optional[float] = None
    error_budget_percent: float = 0.1
    window_days: int = 30
