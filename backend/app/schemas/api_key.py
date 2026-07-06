from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=100
    )

    plan_id: int = Field(
        gt=0
    )

    expires_in_days: int | None = Field(
        default=None,
        ge=1,
        le=3650
    )


class ApiKeyCreateResponse(BaseModel):
    id: int
    name: str
    api_key: str
    key_prefix: str
    plan_name: str
    expires_at: datetime | None
    message: str


class ApiKeyListItem(BaseModel):
    id: int
    name: str
    key_prefix: str
    plan_name: str
    is_active: bool
    expires_at: datetime | None
    created_at: datetime


class PlanListItem(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool