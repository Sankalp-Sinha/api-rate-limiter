from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.admin_auth import require_admin
from app.schemas.api_key import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyListItem,
    PlanListItem,
)
from app.services.api_key_management_service import (
    create_api_key,
    list_api_keys,
    list_plans,
    revoke_api_key,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[
        Depends(require_admin)
    ]
)


@router.get(
    "/plans",
    response_model=list[PlanListItem]
)
def get_plans(
    db: Annotated[
        Session,
        Depends(get_db)
    ]
):
    return list_plans(db)


@router.get(
    "/api-keys",
    response_model=list[ApiKeyListItem]
)
def get_api_keys(
    db: Annotated[
        Session,
        Depends(get_db)
    ]
):
    return list_api_keys(db)


@router.post(
    "/api-keys",
    response_model=ApiKeyCreateResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_api_key(
    payload: ApiKeyCreateRequest,
    db: Annotated[
        Session,
        Depends(get_db)
    ]
):
    result = create_api_key(
        db=db,
        name=payload.name,
        plan_id=payload.plan_id,
        expires_in_days=payload.expires_in_days
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active plan not found"
        )

    return result


@router.post(
    "/api-keys/{api_key_id}/revoke"
)
def revoke_existing_api_key(
    api_key_id: int,
    db: Annotated[
        Session,
        Depends(get_db)
    ]
):
    revoked = revoke_api_key(
        db=db,
        api_key_id=api_key_id
    )

    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    return {
        "message": "API key revoked successfully",
        "api_key_id": api_key_id
    }