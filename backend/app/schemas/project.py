from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=100
    )


class ProjectListItem(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    created_at: datetime


class ProjectDetailResponse(BaseModel):
    id: int
    name: str
    slug: str
    is_active: bool
    created_at: datetime