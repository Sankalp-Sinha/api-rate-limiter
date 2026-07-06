from fastapi import FastAPI
from sqlalchemy import text
from starlette.responses import JSONResponse

from app.db import engine
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.services.redis_client import redis_client


app = FastAPI(
    title="Distributed API Rate Limiter",
    description=(
        "Production-grade API rate limiter using FastAPI, "
        "Redis, PostgreSQL, and Token Bucket algorithm"
    ),
    version="1.0.0",
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
            "ping": response,
        }

    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "redis": "disconnected",
                "message": "Redis health check failed",
            },
        )


@app.get("/health/postgres")
def postgres_health_check():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT 1")
            ).scalar_one()

        return {
            "postgres": "connected",
            "query_result": result,
        }

    except Exception as error:
        return JSONResponse(
            status_code=503,
            content={
                "postgres": "disconnected",
                "message": "PostgreSQL health check failed",
                "error": str(error)
            },
        )


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