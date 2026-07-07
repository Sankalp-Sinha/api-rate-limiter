from fastapi import FastAPI
from sqlalchemy import text
from fastapi import Response
import os
from starlette.responses import JSONResponse
from app.routers.admin import router as admin_router
from app.routers.analytics import router as analytics_router

from fastapi.middleware.trustedhost import (
    TrustedHostMiddleware,
)
from app.routers.health import (
    router as health_router,
)
from app.routers.projects import (
    router as projects_router,
)
from app.routers.project_api_keys import (
    router as project_api_keys_router,
)
from app.routers.project_policies import (
    router as project_policies_router,
)
from app.routers.rate_limit_check import (
    router as rate_limit_check_router,
)
from app.routers.project_analytics import (
    router as project_analytics_router,
)
from app.routers.auth import (
    router as auth_router,
)
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from app.middleware.prometheus_metrics import (
    PrometheusMiddleware,
)

from app.db import engine
from app.services.redis_client import redis_client
from fastapi.middleware.cors import CORSMiddleware


def parse_csv_env(
    name: str,
    default: str = "",
) -> list[str]:
    raw_value = os.getenv(
        name,
        default,
    )

    return [
        item.strip()
        for item in raw_value.split(",")
        if item.strip()
    ]


CORS_ORIGINS = parse_csv_env(
    "CORS_ORIGINS",
    (
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    ),
)

ALLOWED_HOSTS = parse_csv_env(
    "ALLOWED_HOSTS",
    (
        "localhost,"
        "127.0.0.1,"
        "0.0.0.0,"
        "host.docker.internal"
    ),
)


fastapi_app = FastAPI(
    title="Distributed API Rate Limiter",
    description=(
        "Production-grade API rate limiter using FastAPI, "
        "Redis, PostgreSQL, and Token Bucket algorithm"
    ),
    version="1.0.0",
)

ENABLE_METRICS = (
    os.getenv(
        "ENABLE_METRICS",
        "true",
    )
    .strip()
    .lower()
    == "true"
)


if ENABLE_METRICS:

    @fastapi_app.get(
        "/metrics",
        include_in_schema=False,
    )
    def prometheus_metrics():
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )

fastapi_app.add_middleware(
    PrometheusMiddleware
)

fastapi_app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS,
)


fastapi_app.include_router(projects_router)
fastapi_app.include_router(project_api_keys_router)
fastapi_app.include_router(project_policies_router)
fastapi_app.include_router(rate_limit_check_router)
fastapi_app.include_router(project_analytics_router)
fastapi_app.include_router(auth_router)
fastapi_app.include_router(health_router)


app = FastAPI(
    title="Distributed API Rate Limiter",
    description=(
        "Production-grade API rate limiter using FastAPI, "
        "Redis, PostgreSQL, and Token Bucket algorithm"
    ),
    version="1.0.0",
)


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





app = CORSMiddleware(
    app=fastapi_app,

    allow_origins=CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],

    allow_headers=[
        "Authorization",
        "Content-Type",
        "x-admin-key",
        "x-api-key",
    ],

    expose_headers=[
        "X-Request-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "Retry-After",
    ],
)