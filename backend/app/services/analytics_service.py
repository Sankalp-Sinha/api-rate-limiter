from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import ApiKey, RequestLog


def get_analytics_summary(
    db: Session,
    hours: int,
) -> dict:

    since = (
        datetime.now(timezone.utc)
        - timedelta(hours=hours)
    )

    statement = (
        select(
            func.count(
                RequestLog.id
            ).label("total_requests"),

            func.sum(
                case(
                    (
                        RequestLog.allowed.is_(True),
                        1,
                    ),
                    else_=0,
                )
            ).label("allowed_requests"),

            func.sum(
                case(
                    (
                        RequestLog.decision
                        == "rate_limited",
                        1,
                    ),
                    else_=0,
                )
            ).label("rate_limited_requests"),

            func.sum(
                case(
                    (
                        RequestLog.status_code >= 500,
                        1,
                    ),
                    else_=0,
                )
            ).label("server_error_requests"),

            func.avg(
                RequestLog.latency_ms
            ).label("average_latency_ms"),
        )
        .where(
            RequestLog.created_at >= since
        )
    )

    row = db.execute(statement).one()

    return {
        "total_requests": int(
            row.total_requests or 0
        ),
        "allowed_requests": int(
            row.allowed_requests or 0
        ),
        "rate_limited_requests": int(
            row.rate_limited_requests or 0
        ),
        "server_error_requests": int(
            row.server_error_requests or 0
        ),
        "average_latency_ms": round(
            float(row.average_latency_ms or 0),
            3,
        ),
    }


def get_route_analytics(
    db: Session,
    hours: int,
    limit: int,
) -> list[dict]:

    since = (
        datetime.now(timezone.utc)
        - timedelta(hours=hours)
    )

    statement = (
        select(
            RequestLog.route_path,
            RequestLog.http_method,

            func.count(
                RequestLog.id
            ).label("total_requests"),

            func.sum(
                case(
                    (
                        RequestLog.decision
                        == "rate_limited",
                        1,
                    ),
                    else_=0,
                )
            ).label("blocked_requests"),

            func.avg(
                RequestLog.latency_ms
            ).label("average_latency_ms"),
        )
        .where(
            RequestLog.created_at >= since
        )
        .group_by(
            RequestLog.route_path,
            RequestLog.http_method,
        )
        .order_by(
            func.count(
                RequestLog.id
            ).desc()
        )
        .limit(limit)
    )

    rows = db.execute(statement).all()

    return [
        {
            "route_path": row.route_path,
            "http_method": row.http_method,
            "total_requests": int(
                row.total_requests or 0
            ),
            "blocked_requests": int(
                row.blocked_requests or 0
            ),
            "average_latency_ms": round(
                float(
                    row.average_latency_ms or 0
                ),
                3,
            ),
        }
        for row in rows
    ]


def get_api_key_analytics(
    db: Session,
    hours: int,
    limit: int,
) -> list[dict]:

    since = (
        datetime.now(timezone.utc)
        - timedelta(hours=hours)
    )

    statement = (
        select(
            ApiKey.id,
            ApiKey.name,
            ApiKey.key_prefix,

            func.count(
                RequestLog.id
            ).label("total_requests"),

            func.sum(
                case(
                    (
                        RequestLog.decision
                        == "rate_limited",
                        1,
                    ),
                    else_=0,
                )
            ).label("blocked_requests"),
        )
        .join(
            RequestLog,
            RequestLog.api_key_id == ApiKey.id,
        )
        .where(
            RequestLog.created_at >= since
        )
        .group_by(
            ApiKey.id,
            ApiKey.name,
            ApiKey.key_prefix,
        )
        .order_by(
            func.count(
                RequestLog.id
            ).desc()
        )
        .limit(limit)
    )

    rows = db.execute(statement).all()

    return [
        {
            "api_key_id": row.id,
            "name": row.name,
            "key_prefix": row.key_prefix,
            "total_requests": int(
                row.total_requests or 0
            ),
            "blocked_requests": int(
                row.blocked_requests or 0
            ),
        }
        for row in rows
    ]


def get_recent_request_logs(
    db: Session,
    limit: int,
    decision: str | None,
) -> list[RequestLog]:

    statement = select(
        RequestLog
    )

    if decision:
        statement = statement.where(
            RequestLog.decision == decision
        )

    statement = (
        statement
        .order_by(
            RequestLog.created_at.desc()
        )
        .limit(limit)
    )

    return list(
        db.scalars(statement).all()
    )