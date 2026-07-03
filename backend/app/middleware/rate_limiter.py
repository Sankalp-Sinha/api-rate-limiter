from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.redis_client import redis_client
from app.services.redis_token_bucket import RedisTokenBucketLimiter
from app.services.api_key_service import get_api_key_details


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
                    "message": "Missing API key. Please provide x-api-key header."
                }
            )

        api_key_details = get_api_key_details(api_key)

        if not api_key_details:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid API key."
                }
            )

        capacity = api_key_details["capacity"]
        refill_rate = api_key_details["refill_rate"]
        plan = api_key_details["plan"]

        limiter = RedisTokenBucketLimiter(
            redis_client=redis_client,
            capacity=capacity,
            refill_rate=refill_rate
        )

        key = f"api_key:{api_key}:{request.url.path}"

        allowed, remaining, retry_after, reset_after = await limiter.allow_request(key)

        headers = {
            "X-RateLimit-Limit": str(capacity),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_after),
            "X-RateLimit-Plan": plan
        }

        if not allowed:
            headers["Retry-After"] = str(retry_after)

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded. Please try again later.",
                    "plan": plan,
                    "retry_after_seconds": retry_after
                },
                headers=headers
            )

        response = await call_next(request)

        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

        return response