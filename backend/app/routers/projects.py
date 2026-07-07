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
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectListItem,
)
from app.services.project_service import (
    create_project,
    get_project,
    list_projects,
)


router = APIRouter(
    prefix="/admin/projects",
    tags=["Projects"],
)


@router.post(
    "",
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_endpoint(
    payload: ProjectCreateRequest,

    current_user: User = Depends(
        require_admin
    ),
):
    return create_project(
        name=payload.name,
        owner_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[
        ProjectListItem
    ],
)
def list_projects_endpoint(
    current_user: User = Depends(
        require_admin
    ),
):
    return list_projects(
        owner_id=current_user.id
    )


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
)
def get_project_endpoint(
    project_id: int,

    current_user: User = Depends(
        require_admin
    ),
):
    project = get_project(
        project_id=project_id,
        owner_id=current_user.id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project