from datetime import datetime

from pydantic import BaseModel, Field


class ProjectApiKeyCreateRequest(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=100,
    )


class ProjectApiKeyCreatedResponse(BaseModel):
    id: int
    project_id: int
    name: str
    api_key: str
    key_prefix: str
    is_active: bool
    expires_at: datetime | None
    created_at: datetime
    message: str


class ProjectApiKeyListItem(BaseModel):
    id: int
    project_id: int
    name: str
    key_prefix: str
    is_active: bool
    expires_at: datetime | None
    created_at: datetime