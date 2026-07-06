from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


HttpMethod = Literal[
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
]

RefillUnit = Literal[
    "second",
    "minute",
    "hour",
]


class ProjectPolicyCreateRequest(BaseModel):
    route_path: str = Field(
        min_length=1,
        max_length=255,
    )

    http_method: HttpMethod

    capacity: int = Field(
        ge=1,
        le=1_000_000,
    )

    refill_amount: float = Field(
        gt=0,
        le=1_000_000,
    )

    refill_unit: RefillUnit

    tokens_required: int = Field(
        default=1,
        ge=1,
        le=1_000_000,
    )


class ProjectPolicyUpdateRequest(BaseModel):
    capacity: int = Field(
        ge=1,
        le=1_000_000,
    )

    refill_amount: float = Field(
        gt=0,
        le=1_000_000,
    )

    refill_unit: RefillUnit

    tokens_required: int = Field(
        default=1,
        ge=1,
        le=1_000_000,
    )


class ProjectPolicyResponse(BaseModel):
    id: int
    project_id: int
    route_path: str
    http_method: str
    capacity: int
    refill_rate: float
    refill_amount: float
    refill_unit: str
    tokens_required: int
    is_active: bool
    created_at: datetime