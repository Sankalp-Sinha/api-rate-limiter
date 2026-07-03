from fastapi import FastAPI

from app.middleware.rate_limiter import RateLimiterMiddleware
from app.services.redis_client import redis_client


app = FastAPI(
    title="Distributed API Rate Limiter",
    description="Production-grade API rate limiter using FastAPI, Redis, PostgreSQL, and Token Bucket algorithm",
    version="1.0.0"
)

app.add_middleware(RateLimiterMiddleware)


@app.get("/")
def health_check():
    return {
        "message": "API Rate Limiter backend is running"
    }


@app.get("/health/redis")
async def redis_health_check():
    try:
        response = await redis_client.ping()

        return {
            "redis": "connected",
            "ping": response
        }

    except Exception as error:
        return {
            "redis": "disconnected",
            "error": str(error)
        }


@app.get("/api/public")
def public_api():
    return {
        "message": "This is a public API endpoint"
    }


@app.get("/api/protected")
def protected_api():
    return {
        "message": "This is a protected API endpoint"
    }