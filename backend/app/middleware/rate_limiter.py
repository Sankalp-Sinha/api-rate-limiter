from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.redis_client import redis_client
from app.services.redis_token_bucket import RedisTokenBucketLimiter


limiter = RedisTokenBucketLimiter(
    redis_client=redis_client,
    capacity=5,
    refill_rate=1
)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rate_limited_paths = [
            "/api/protected"
        ]

        if request.url.path not in rate_limited_paths:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{request.url.path}"

        allowed, remaining, retry_after, reset_after = await limiter.allow_request(key)

        headers = {
            "X-RateLimit-Limit": str(limiter.capacity),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_after),
        }

        if not allowed:
            headers["Retry-After"] = str(retry_after)

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded. Please try again later.",
                    "retry_after_seconds": retry_after
                },
                headers=headers
            )

        response = await call_next(request)

        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

        return response