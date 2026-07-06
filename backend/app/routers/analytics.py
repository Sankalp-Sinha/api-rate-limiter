from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.admin_auth import require_admin
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    ApiKeyAnalyticsItem,
    RequestLogItem,
    RouteAnalyticsItem,
)
from app.services.analytics_service import (
    get_analytics_summary,
    get_api_key_analytics,
    get_recent_request_logs,
    get_route_analytics,
)


router = APIRouter(
    prefix="/admin/analytics",
    tags=["Analytics"],
    dependencies=[
        Depends(require_admin)
    ],
)


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
)
def analytics_summary(
    db: Annotated[
        Session,
        Depends(get_db)
    ],
    hours: int = Query(
        default=24,
        ge=1,
        le=720,
    ),
):
    return get_analytics_summary(
        db=db,
        hours=hours,
    )


@router.get(
    "/routes",
    response_model=list[RouteAnalyticsItem],
)
def route_analytics(
    db: Annotated[
        Session,
        Depends(get_db)
    ],
    hours: int = Query(
        default=24,
        ge=1,
        le=720,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
):
    return get_route_analytics(
        db=db,
        hours=hours,
        limit=limit,
    )


@router.get(
    "/api-keys",
    response_model=list[ApiKeyAnalyticsItem],
)
def api_key_analytics(
    db: Annotated[
        Session,
        Depends(get_db)
    ],
    hours: int = Query(
        default=24,
        ge=1,
        le=720,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
):
    return get_api_key_analytics(
        db=db,
        hours=hours,
        limit=limit,
    )


@router.get(
    "/request-logs",
    response_model=list[RequestLogItem],
)
def recent_request_logs(
    db: Annotated[
        Session,
        Depends(get_db)
    ],
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
    decision: str | None = Query(
        default=None
    ),
):
    return get_recent_request_logs(
        db=db,
        limit=limit,
        decision=decision,
    )