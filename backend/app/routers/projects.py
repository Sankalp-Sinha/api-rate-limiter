from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.dependencies.admin_auth import (
    require_admin,
)
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
    dependencies=[
        Depends(require_admin)
    ],
)


@router.post(
    "",
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_endpoint(
    payload: ProjectCreateRequest
):
    return create_project(
        name=payload.name
    )


@router.get(
    "",
    response_model=list[ProjectListItem],
)
def list_projects_endpoint():
    return list_projects()


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
)
def get_project_endpoint(
    project_id: int
):
    project = get_project(
        project_id=project_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project