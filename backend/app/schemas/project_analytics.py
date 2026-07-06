from datetime import datetime

from pydantic import BaseModel


class ProjectAnalyticsSummaryResponse(BaseModel):
    project_id: int
    hours: int

    total_checks: int
    allowed_checks: int
    blocked_checks: int

    block_rate_percent: float
    unique_subjects: int
    average_latency_ms: float

    active_endpoints: int


class EndpointAnalyticsItem(BaseModel):
    policy_id: int
    project_id: int

    route_path: str
    http_method: str

    capacity: int
    refill_amount: float
    refill_unit: str

    is_active: bool

    total_checks: int
    allowed_checks: int
    blocked_checks: int

    block_rate_percent: float
    unique_subjects: int
    average_latency_ms: float

    last_request_at: datetime | None