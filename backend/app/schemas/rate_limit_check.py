from typing import Literal

from pydantic import BaseModel, Field


HttpMethod = Literal[
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
]


class RateLimitCheckRequest(BaseModel):
    subject: str = Field(
        min_length=1,
        max_length=255,
    )

    route: str = Field(
        min_length=1,
        max_length=255,
    )

    method: HttpMethod


class RateLimitCheckResponse(BaseModel):
    allowed: bool

    request_id: str

    project_id: int
    policy_id: int

    route: str
    method: str

    limit: int
    remaining: int

    retry_after_seconds: int
    reset_after_seconds: int