from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.api_key_service import get_rate_limit_context
from app.services.redis_client import redis_client
from app.services.redis_token_bucket import RedisTokenBucketLimiter
from app.services.request_log_service import safe_write_request_log


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rate_limited_paths = [
            "/api/protected"
        ]

        if request.url.path not in rate_limited_paths:
            return await call_next(request)

        request_id = str(uuid4())
        started_at = perf_counter()

        async def persist_log(
            *,
            api_key_id: int | None,
            plan_name: str | None,
            decision: str,
            status_code: int,
            allowed: bool,
            remaining_tokens: int | None = None,
            retry_after_seconds: int | None = None,
        ) -> None:

            latency_ms = round(
                (perf_counter() - started_at) * 1000,
                3,
            )

            await run_in_threadpool(
                safe_write_request_log,
                request_id=request_id,
                api_key_id=api_key_id,
                plan_name=plan_name,
                route_path=request.url.path,
                http_method=request.method,
                decision=decision,
                status_code=status_code,
                allowed=allowed,
                remaining_tokens=remaining_tokens,
                retry_after_seconds=retry_after_seconds,
                latency_ms=latency_ms,
            )

        api_key = request.headers.get("x-api-key")

        # -----------------------------
        # Missing API key
        # -----------------------------
        if not api_key:
            await persist_log(
                api_key_id=None,
                plan_name=None,
                decision="missing_api_key",
                status_code=401,
                allowed=False,
            )

            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": (
                        "Missing API key. "
                        "Please provide x-api-key header."
                    ),
                },
                headers={
                    "X-Request-ID": request_id,
                },
            )

        # -----------------------------
        # PostgreSQL key + plan + policy
        # lookup
        # -----------------------------
        lookup_status, context = await run_in_threadpool(
            get_rate_limit_context,
            api_key,
            request.url.path,
            request.method,
        )

        # -----------------------------
        # Invalid key
        # -----------------------------
        if lookup_status == "invalid_key":
            await persist_log(
                api_key_id=None,
                plan_name=None,
                decision="invalid_api_key",
                status_code=401,
                allowed=False,
            )

            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid or inactive API key.",
                },
                headers={
                    "X-Request-ID": request_id,
                },
            )

        # -----------------------------
        # No matching policy
        # -----------------------------
        if lookup_status == "no_policy":
            await persist_log(
                api_key_id=None,
                plan_name=None,
                decision="no_policy",
                status_code=403,
                allowed=False,
            )

            return JSONResponse(
                status_code=403,
                content={
                    "error": "Forbidden",
                    "message": (
                        "No active rate-limit policy "
                        "exists for this route."
                    ),
                },
                headers={
                    "X-Request-ID": request_id,
                },
            )

        # -----------------------------
        # Unexpected lookup state
        # -----------------------------
        if context is None:
            await persist_log(
                api_key_id=None,
                plan_name=None,
                decision="internal_error",
                status_code=500,
                allowed=False,
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error"
                },
                headers={
                    "X-Request-ID": request_id,
                },
            )

        # -----------------------------
        # Create Redis Token Bucket
        # from PostgreSQL policy
        # -----------------------------
        limiter = RedisTokenBucketLimiter(
            redis_client=redis_client,
            capacity=context.capacity,
            refill_rate=context.refill_rate,
        )

        redis_bucket_key = (
            f"api_key_id:{context.api_key_id}:"
            f"{request.method}:{request.url.path}"
        )

        (
            allowed,
            remaining,
            retry_after,
            reset_after,
        ) = await limiter.allow_request(
            redis_bucket_key,
            tokens_required=context.tokens_required,
        )

        rate_limit_headers = {
            "X-RateLimit-Limit": str(context.capacity),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_after),
            "X-RateLimit-Plan": context.plan_name,
            "X-Request-ID": request_id,
        }

        # -----------------------------
        # Blocked by rate limiter
        # -----------------------------
        if not allowed:
            await persist_log(
                api_key_id=context.api_key_id,
                plan_name=context.plan_name,
                decision="rate_limited",
                status_code=429,
                allowed=False,
                remaining_tokens=remaining,
                retry_after_seconds=retry_after,
            )

            rate_limit_headers["Retry-After"] = str(
                retry_after
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": (
                        "Rate limit exceeded. "
                        "Please try again later."
                    ),
                    "plan": context.plan_name,
                    "retry_after_seconds": retry_after,
                },
                headers=rate_limit_headers,
            )

        # -----------------------------
        # Allowed: run real endpoint
        # -----------------------------
        try:
            response = await call_next(request)

        except Exception:
            await persist_log(
                api_key_id=context.api_key_id,
                plan_name=context.plan_name,
                decision="endpoint_error",
                status_code=500,
                allowed=True,
                remaining_tokens=remaining,
            )

            raise

        for header_name, header_value in (
            rate_limit_headers.items()
        ):
            response.headers[header_name] = header_value

        await persist_log(
            api_key_id=context.api_key_id,
            plan_name=context.plan_name,
            decision="allowed",
            status_code=response.status_code,
            allowed=True,
            remaining_tokens=remaining,
        )

        return response