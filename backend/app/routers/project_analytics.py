from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.dependencies.admin_auth import (
    require_admin,
)
from app.models.user import User
from app.schemas.project_analytics import (
    EndpointAnalyticsItem,
    ProjectAnalyticsSummaryResponse,
)
from app.services.project_analytics_service import (
    get_project_analytics_summary,
    get_project_endpoint_analytics,
)
from app.services.project_service import (
    get_project,
)


router = APIRouter(
    prefix="/admin/projects",
    tags=["Project Analytics"],
)


@router.get(
    "/{project_id}/analytics/summary",
    response_model=(
        ProjectAnalyticsSummaryResponse
    ),
)
def get_project_summary_endpoint(
    project_id: int,

    hours: int = Query(
        default=24,
        ge=1,
        le=720,
    ),

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

    return get_project_analytics_summary(
        project_id=project_id,
        hours=hours,
    )


@router.get(
    "/{project_id}/analytics/endpoints",
    response_model=list[
        EndpointAnalyticsItem
    ],
)
def get_endpoint_analytics_endpoint(
    project_id: int,

    hours: int = Query(
        default=24,
        ge=1,
        le=720,
    ),

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

    return get_project_endpoint_analytics(
        project_id=project_id,
        hours=hours,
    )