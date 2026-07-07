from fastapi import APIRouter
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from app.db import SessionLocal
from app.services.redis_client import redis_client


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/live")
def liveness():
    return {
        "status": "alive"
    }


def check_postgres() -> bool:
    try:
        with SessionLocal() as db:
            db.execute(
                text("SELECT 1")
            )

        return True

    except Exception:
        return False


@router.get("/ready")
async def readiness():
    checks = {
        "postgres": False,
        "redis": False,
    }

    checks["postgres"] = (
        await run_in_threadpool(
            check_postgres
        )
    )

    try:
        await redis_client.ping()
        checks["redis"] = True

    except Exception:
        checks["redis"] = False

    ready = all(checks.values())

    payload = {
        "status": (
            "ready"
            if ready
            else "not_ready"
        ),
        "checks": checks,
    }

    if not ready:
        return JSONResponse(
            status_code=503,
            content=payload,
        )

    return payload