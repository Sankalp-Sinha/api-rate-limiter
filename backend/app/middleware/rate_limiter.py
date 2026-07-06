from fastapi import Request
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.api_key_service import get_rate_limit_context
from app.services.redis_client import redis_client
from app.services.redis_token_bucket import RedisTokenBucketLimiter


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rate_limited_paths = [
            "/api/protected"
        ]

        if request.url.path not in rate_limited_paths:
            return await call_next(request)

        api_key = request.headers.get("x-api-key")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": (
                        "Missing API key. "
                        "Please provide x-api-key header."
                    )
                }
            )

        lookup_status, context = await run_in_threadpool(
            get_rate_limit_context,
            api_key,
            request.url.path,
            request.method
        )

        if lookup_status == "invalid_key":
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid or inactive API key."
                }
            )

        if lookup_status == "no_policy":
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Forbidden",
                    "message": (
                        "No active rate-limit policy "
                        "exists for this route."
                    )
                }
            )

        if context is None:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error"
                }
            )

        limiter = RedisTokenBucketLimiter(
            redis_client=redis_client,
            capacity=context.capacity,
            refill_rate=context.refill_rate
        )

        redis_bucket_key = (
            f"api_key_id:{context.api_key_id}:"
            f"{request.method}:{request.url.path}"
        )

        allowed, remaining, retry_after, reset_after = (
            await limiter.allow_request(
                redis_bucket_key,
                tokens_required=context.tokens_required
            )
        )

        headers = {
            "X-RateLimit-Limit": str(context.capacity),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_after),
            "X-RateLimit-Plan": context.plan_name
        }

        if not allowed:
            headers["Retry-After"] = str(retry_after)

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": (
                        "Rate limit exceeded. "
                        "Please try again later."
                    ),
                    "plan": context.plan_name,
                    "retry_after_seconds": retry_after
                },
                headers=headers
            )

        response = await call_next(request)

        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

        return response