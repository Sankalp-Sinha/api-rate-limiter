from time import perf_counter
from uuid import uuid4

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
)
from starlette.concurrency import (
    run_in_threadpool,
)

from app.schemas.rate_limit_check import (
    RateLimitCheckRequest,
    RateLimitCheckResponse,
)
from app.services.check_request_log_service import (
    safe_write_check_request_log,
)
from app.services.project_key_auth_service import (
    authenticate_project_key,
)
from app.services.project_policy_lookup_service import (
    get_active_project_policy,
)
from app.services.project_policy_service import (
    normalize_route_path,
)
from app.services.subject_service import (
    build_subject_bucket_key,
    hash_subject,
)
from app.services.subject_token_bucket import (
    consume_subject_bucket,
)


router = APIRouter(
    prefix="/v1",
    tags=["Rate Limit Check"],
)


def extract_bearer_token(
    authorization: str | None,
) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail=(
                "Missing Authorization header"
            ),
        )

    scheme, separator, token = (
        authorization.partition(" ")
    )

    if (
        separator == ""
        or scheme.lower() != "bearer"
        or not token.strip()
    ):
        raise HTTPException(
            status_code=401,
            detail=(
                "Expected Authorization: "
                "Bearer <project-key>"
            ),
        )

    return token.strip()


@router.post(
    "/check",
    response_model=RateLimitCheckResponse,
)
async def check_rate_limit(
    payload: RateLimitCheckRequest,
    authorization: str | None = Header(
        default=None,
        alias="Authorization",
    ),
):
    started_at = perf_counter()

    request_id = str(uuid4())

    raw_api_key = extract_bearer_token(
        authorization
    )

    key_context = await run_in_threadpool(
        authenticate_project_key,
        raw_api_key,
    )

    if key_context is None:
        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid or inactive "
                "project integration key"
            ),
        )

    normalized_route = (
        normalize_route_path(
            payload.route
        )
    )

    normalized_method = (
        payload.method.upper()
    )

    policy = await run_in_threadpool(
        get_active_project_policy,
        key_context.project_id,
        key_context.plan_id,
        normalized_route,
        normalized_method,
    )

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No active rate-limit policy "
                "configured for this project, "
                "route, and method"
            ),
        )

    subject_hash = hash_subject(
        payload.subject
    )

    redis_key = build_subject_bucket_key(
        project_id=(
            key_context.project_id
        ),
        policy_id=policy.id,
        subject_hash=subject_hash,
    )

    decision = await consume_subject_bucket(
        redis_key=redis_key,
        capacity=policy.capacity,
        refill_rate=policy.refill_rate,
        tokens_required=(
            policy.tokens_required
        ),
    )

    latency_ms = (
        perf_counter() - started_at
    ) * 1000

    await run_in_threadpool(
        safe_write_check_request_log,
        request_id=request_id,
        api_key_id=(
            key_context.api_key_id
        ),
        project_id=(
            key_context.project_id
        ),
        policy_id=policy.id,
        subject_hash=subject_hash,
        plan_name=(
            key_context.plan_name
        ),
        route_path=normalized_route,
        http_method=normalized_method,
        allowed=decision.allowed,
        remaining_tokens=(
            decision.remaining
        ),
        retry_after_seconds=(
            decision.retry_after_seconds
        ),
        latency_ms=latency_ms,
    )

    return RateLimitCheckResponse(
        allowed=decision.allowed,
        request_id=request_id,
        project_id=(
            key_context.project_id
        ),
        policy_id=policy.id,
        route=normalized_route,
        method=normalized_method,
        limit=policy.capacity,
        remaining=decision.remaining,
        retry_after_seconds=(
            decision.retry_after_seconds
        ),
        reset_after_seconds=(
            decision.reset_after_seconds
        ),
    )