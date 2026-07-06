from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.dependencies.admin_auth import (
    require_admin,
)
from app.schemas.project_policy import (
    ProjectPolicyCreateRequest,
    ProjectPolicyResponse,
    ProjectPolicyUpdateRequest,
)
from app.services.project_policy_service import (
    create_project_policy,
    deactivate_project_policy,
    list_project_policies,
    update_project_policy,
)


router = APIRouter(
    prefix="/admin/projects",
    tags=["Project Policies"],
    dependencies=[
        Depends(require_admin)
    ],
)


@router.get(
    "/{project_id}/policies",
    response_model=list[
        ProjectPolicyResponse
    ],
)
def list_project_policies_endpoint(
    project_id: int,
):
    return list_project_policies(
        project_id=project_id
    )


@router.post(
    "/{project_id}/policies",
    response_model=ProjectPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_policy_endpoint(
    project_id: int,
    payload: ProjectPolicyCreateRequest,
):
    result_status, policy = (
        create_project_policy(
            project_id=project_id,
            route_path=payload.route_path,
            http_method=payload.http_method,
            capacity=payload.capacity,
            refill_amount=(
                payload.refill_amount
            ),
            refill_unit=(
                payload.refill_unit
            ),
            tokens_required=(
                payload.tokens_required
            ),
        )
    )

    if (
        result_status
        == "project_not_found"
    ):
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    if (
        result_status
        == "free_plan_not_found"
    ):
        raise HTTPException(
            status_code=500,
            detail=(
                "Active free plan "
                "not configured"
            ),
        )

    if result_status == "duplicate":
        raise HTTPException(
            status_code=409,
            detail=(
                "A policy already exists "
                "for this project, route, "
                "and HTTP method"
            ),
        )

    return policy


@router.put(
    "/{project_id}/policies/{policy_id}",
    response_model=ProjectPolicyResponse,
)
def update_project_policy_endpoint(
    project_id: int,
    policy_id: int,
    payload: ProjectPolicyUpdateRequest,
):
    policy = update_project_policy(
        project_id=project_id,
        policy_id=policy_id,
        capacity=payload.capacity,
        refill_amount=(
            payload.refill_amount
        ),
        refill_unit=payload.refill_unit,
        tokens_required=(
            payload.tokens_required
        ),
    )

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Policy not found "
                "for this project"
            ),
        )

    return policy


@router.post(
    "/{project_id}/policies/"
    "{policy_id}/deactivate",
    response_model=ProjectPolicyResponse,
)
def deactivate_project_policy_endpoint(
    project_id: int,
    policy_id: int,
):
    policy = deactivate_project_policy(
        project_id=project_id,
        policy_id=policy_id,
    )

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Policy not found "
                "for this project"
            ),
        )

    return policy