from app.db import SessionLocal
from app.models import RequestLog


def write_request_log(
    *,
    request_id: str,
    api_key_id: int | None,
    plan_name: str | None,
    route_path: str,
    http_method: str,
    decision: str,
    status_code: int,
    allowed: bool,
    remaining_tokens: int | None,
    retry_after_seconds: int | None,
    latency_ms: float,
) -> None:

    with SessionLocal() as db:
        request_log = RequestLog(
            request_id=request_id,
            api_key_id=api_key_id,
            plan_name=plan_name,
            route_path=route_path,
            http_method=http_method,
            decision=decision,
            status_code=status_code,
            allowed=allowed,
            remaining_tokens=remaining_tokens,
            retry_after_seconds=retry_after_seconds,
            latency_ms=latency_ms,
        )

        db.add(request_log)
        db.commit()


def safe_write_request_log(**kwargs) -> None:
    try:
        write_request_log(**kwargs)

    except Exception as error:
        # Logging failure must not break the actual API request.
        print(
            "Request log persistence failed:",
            str(error),
        )