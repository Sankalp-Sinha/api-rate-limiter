from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.dependencies.admin_auth import (
    require_admin,
)
from app.models.user import User
from app.schemas.project_api_key import (
    ProjectApiKeyCreateRequest,
    ProjectApiKeyCreatedResponse,
    ProjectApiKeyListItem,
)
from app.services.project_api_key_service import (
    create_project_api_key,
    list_project_api_keys,
    revoke_project_api_key,
)


router = APIRouter(
    prefix="/admin/projects",
    tags=["Project API Keys"],
)


@router.get(
    "/{project_id}/api-keys",
    response_model=list[
        ProjectApiKeyListItem
    ],
)
def get_project_api_keys_endpoint(
    project_id: int,

    current_user: User = Depends(
        require_admin
    ),
):
    api_keys = list_project_api_keys(
        project_id=project_id,
        owner_id=current_user.id,
    )

    if api_keys is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return api_keys


@router.post(
    "/{project_id}/api-keys",
    response_model=(
        ProjectApiKeyCreatedResponse
    ),
    status_code=status.HTTP_201_CREATED,
)
def create_project_api_key_endpoint(
    project_id: int,
    payload: ProjectApiKeyCreateRequest,

    current_user: User = Depends(
        require_admin
    ),
):
    result = create_project_api_key(
        project_id=project_id,
        owner_id=current_user.id,
        name=payload.name,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Project not found "
                "or inactive"
            ),
        )

    return result


@router.post(
    "/{project_id}/api-keys/"
    "{api_key_id}/revoke",
)
def revoke_project_api_key_endpoint(
    project_id: int,
    api_key_id: int,

    current_user: User = Depends(
        require_admin
    ),
):
    api_key = revoke_project_api_key(
        project_id=project_id,
        api_key_id=api_key_id,
        owner_id=current_user.id,
    )

    if api_key is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "API key not found "
                "for this project"
            ),
        )

    return {
        "success": True,
        "message": "API key revoked",
        "api_key_id": api_key.id,
    }