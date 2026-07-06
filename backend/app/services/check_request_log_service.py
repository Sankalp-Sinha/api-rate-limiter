from app.db import SessionLocal
from app.models.request_log import (
    RequestLog,
)


def write_check_request_log(
    *,
    request_id: str,
    api_key_id: int,
    project_id: int,
    policy_id: int,
    subject_hash: str,
    plan_name: str,
    route_path: str,
    http_method: str,
    allowed: bool,
    remaining_tokens: int,
    retry_after_seconds: int,
    latency_ms: float,
) -> None:
    with SessionLocal() as db:
        log = RequestLog(
            request_id=request_id,
            api_key_id=api_key_id,
            project_id=project_id,
            policy_id=policy_id,
            subject_hash=subject_hash,
            plan_name=plan_name,
            route_path=route_path,
            http_method=http_method,
            decision=(
                "allowed"
                if allowed
                else "rate_limited"
            ),

            # This represents the rate-limit
            # decision, not the HTTP status of
            # /v1/check itself.
            status_code=(
                200
                if allowed
                else 429
            ),

            allowed=allowed,
            remaining_tokens=(
                remaining_tokens
            ),
            retry_after_seconds=(
                retry_after_seconds
            ),
            latency_ms=latency_ms,
        )

        db.add(log)
        db.commit()


def safe_write_check_request_log(
    **kwargs,
) -> None:
    try:
        write_check_request_log(
            **kwargs
        )
    except Exception as error:
        # Logging must never break the actual
        # rate-limit decision.
        print(
            "Check request logging failed:",
            error,
        )