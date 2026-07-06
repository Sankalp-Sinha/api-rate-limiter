from fastapi import FastAPI
from sqlalchemy import text
from starlette.responses import JSONResponse
from app.routers.admin import router as admin_router
from app.routers.analytics import router as analytics_router

from app.db import engine
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.services.redis_client import redis_client
from fastapi.middleware.cors import CORSMiddleware


fastapi_app = FastAPI(
    title="Distributed API Rate Limiter",
    description=(
        "Production-grade API rate limiter using FastAPI, "
        "Redis, PostgreSQL, and Token Bucket algorithm"
    ),
    version="1.0.0",
)

fastapi_app.add_middleware(
    RateLimiterMiddleware
)


fastapi_app.include_router(admin_router)
fastapi_app.include_router(analytics_router)


app = FastAPI(
    title="Distributed API Rate Limiter",
    description=(
        "Production-grade API rate limiter using FastAPI, "
        "Redis, PostgreSQL, and Token Bucket algorithm"
    ),
    version="1.0.0",
)


app.add_middleware(RateLimiterMiddleware)
app.include_router(admin_router)
app.include_router(analytics_router)

@fastapi_app.get("/")
def health_check():
    return {
        "message": "API Rate Limiter backend is running"
    }


@fastapi_app.get("/health/redis")
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


@fastapi_app.get("/health/postgres")
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


@fastapi_app.get("/api/public")
def public_api():
    return {
        "message": "This is a public API endpoint"
    }


@fastapi_app.get("/api/protected")
def protected_api():
    return {
        "message": "This is a protected API endpoint"
    }



app = CORSMiddleware(
    app=fastapi_app,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "X-RateLimit-Plan",
        "X-Request-ID",
        "Retry-After",
    ],
)