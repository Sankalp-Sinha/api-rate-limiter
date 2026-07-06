from datetime import datetime

from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    total_requests: int
    allowed_requests: int
    rate_limited_requests: int
    server_error_requests: int
    average_latency_ms: float


class RouteAnalyticsItem(BaseModel):
    route_path: str
    http_method: str
    total_requests: int
    blocked_requests: int
    average_latency_ms: float


class ApiKeyAnalyticsItem(BaseModel):
    api_key_id: int
    name: str
    key_prefix: str
    total_requests: int
    blocked_requests: int


class RequestLogItem(BaseModel):
    request_id: str
    api_key_id: int | None
    plan_name: str | None
    route_path: str
    http_method: str
    decision: str
    status_code: int
    allowed: bool
    remaining_tokens: int | None
    retry_after_seconds: int | None
    latency_ms: float
    created_at: datetime