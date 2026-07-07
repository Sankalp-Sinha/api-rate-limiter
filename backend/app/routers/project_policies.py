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
)


@router.get(
    "/{project_id}/policies",
    response_model=list[
        ProjectPolicyResponse
    ],
)
def list_project_policies_endpoint(
    project_id: int,

    current_user: User = Depends(
        require_admin
    ),
):
    policies = list_project_policies(
        project_id=project_id,
        owner_id=current_user.id,
    )

    if policies is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return policies


@router.post(
    "/{project_id}/policies",
    response_model=ProjectPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_policy_endpoint(
    project_id: int,
    payload: ProjectPolicyCreateRequest,

    current_user: User = Depends(
        require_admin
    ),
):
    result_status, policy = (
        create_project_policy(
            project_id=project_id,
            owner_id=current_user.id,
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

    current_user: User = Depends(
        require_admin
    ),
):
    policy = update_project_policy(
        project_id=project_id,
        policy_id=policy_id,
        owner_id=current_user.id,
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

    current_user: User = Depends(
        require_admin
    ),
):
    policy = deactivate_project_policy(
        project_id=project_id,
        policy_id=policy_id,
        owner_id=current_user.id,
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