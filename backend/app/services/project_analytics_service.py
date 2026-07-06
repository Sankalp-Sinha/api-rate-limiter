from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy import (
    case,
    func,
    select,
)

from app.db import SessionLocal
from app.models.rate_limit_policy import (
    RateLimitPolicy,
)
from app.models.request_log import (
    RequestLog,
)


def get_cutoff_time(
    hours: int,
) -> datetime:
    return (
        datetime.now(timezone.utc)
        - timedelta(hours=hours)
    )


def get_project_analytics_summary(
    project_id: int,
    hours: int,
) -> dict:
    cutoff = get_cutoff_time(hours)

    with SessionLocal() as db:
        row = db.execute(
            select(
                func.count(
                    RequestLog.id
                ).label(
                    "total_checks"
                ),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                RequestLog.allowed
                                .is_(True),
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label(
                    "allowed_checks"
                ),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                RequestLog.allowed
                                .is_(False),
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label(
                    "blocked_checks"
                ),

                func.count(
                    func.distinct(
                        RequestLog.subject_hash
                    )
                ).label(
                    "unique_subjects"
                ),

                func.coalesce(
                    func.avg(
                        RequestLog.latency_ms
                    ),
                    0.0,
                ).label(
                    "average_latency_ms"
                ),
            )
            .where(
                RequestLog.project_id
                == project_id,

                RequestLog.created_at
                >= cutoff,
            )
        ).mappings().one()

        active_endpoints = db.scalar(
            select(
                func.count(
                    RateLimitPolicy.id
                )
            ).where(
                RateLimitPolicy.project_id
                == project_id,

                RateLimitPolicy.is_active
                .is_(True),
            )
        )

        total_checks = int(
            row["total_checks"] or 0
        )

        allowed_checks = int(
            row["allowed_checks"] or 0
        )

        blocked_checks = int(
            row["blocked_checks"] or 0
        )

        unique_subjects = int(
            row["unique_subjects"] or 0
        )

        average_latency_ms = round(
            float(
                row["average_latency_ms"]
                or 0.0
            ),
            2,
        )

        block_rate_percent = (
            round(
                (
                    blocked_checks
                    / total_checks
                ) * 100,
                2,
            )
            if total_checks > 0
            else 0.0
        )

        return {
            "project_id": project_id,
            "hours": hours,

            "total_checks": total_checks,
            "allowed_checks": allowed_checks,
            "blocked_checks": blocked_checks,

            "block_rate_percent": (
                block_rate_percent
            ),

            "unique_subjects": (
                unique_subjects
            ),

            "average_latency_ms": (
                average_latency_ms
            ),

            "active_endpoints": int(
                active_endpoints or 0
            ),
        }


def get_project_endpoint_analytics(
    project_id: int,
    hours: int,
) -> list[dict]:
    cutoff = get_cutoff_time(hours)

    with SessionLocal() as db:
        log_aggregation = (
            select(
                RequestLog.policy_id.label(
                    "policy_id"
                ),

                func.count(
                    RequestLog.id
                ).label(
                    "total_checks"
                ),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                RequestLog.allowed
                                .is_(True),
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label(
                    "allowed_checks"
                ),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                RequestLog.allowed
                                .is_(False),
                                1,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label(
                    "blocked_checks"
                ),

                func.count(
                    func.distinct(
                        RequestLog.subject_hash
                    )
                ).label(
                    "unique_subjects"
                ),

                func.coalesce(
                    func.avg(
                        RequestLog.latency_ms
                    ),
                    0.0,
                ).label(
                    "average_latency_ms"
                ),

                func.max(
                    RequestLog.created_at
                ).label(
                    "last_request_at"
                ),
            )
            .where(
                RequestLog.project_id
                == project_id,

                RequestLog.created_at
                >= cutoff,
            )
            .group_by(
                RequestLog.policy_id
            )
            .subquery()
        )

        rows = db.execute(
            select(
                RateLimitPolicy.id.label(
                    "policy_id"
                ),

                RateLimitPolicy.project_id
                .label(
                    "project_id"
                ),

                RateLimitPolicy.route_path
                .label(
                    "route_path"
                ),

                RateLimitPolicy.http_method
                .label(
                    "http_method"
                ),

                RateLimitPolicy.capacity
                .label(
                    "capacity"
                ),

                RateLimitPolicy.refill_amount
                .label(
                    "refill_amount"
                ),

                RateLimitPolicy.refill_unit
                .label(
                    "refill_unit"
                ),

                RateLimitPolicy.is_active
                .label(
                    "is_active"
                ),

                func.coalesce(
                    log_aggregation.c
                    .total_checks,
                    0,
                ).label(
                    "total_checks"
                ),

                func.coalesce(
                    log_aggregation.c
                    .allowed_checks,
                    0,
                ).label(
                    "allowed_checks"
                ),

                func.coalesce(
                    log_aggregation.c
                    .blocked_checks,
                    0,
                ).label(
                    "blocked_checks"
                ),

                func.coalesce(
                    log_aggregation.c
                    .unique_subjects,
                    0,
                ).label(
                    "unique_subjects"
                ),

                func.coalesce(
                    log_aggregation.c
                    .average_latency_ms,
                    0.0,
                ).label(
                    "average_latency_ms"
                ),

                log_aggregation.c
                .last_request_at
                .label(
                    "last_request_at"
                ),
            )
            .outerjoin(
                log_aggregation,

                log_aggregation.c.policy_id
                == RateLimitPolicy.id,
            )
            .where(
                RateLimitPolicy.project_id
                == project_id
            )
            .order_by(
                RateLimitPolicy
                .created_at
                .desc()
            )
        ).mappings().all()

        result: list[dict] = []

        for row in rows:
            total_checks = int(
                row["total_checks"] or 0
            )

            allowed_checks = int(
                row["allowed_checks"] or 0
            )

            blocked_checks = int(
                row["blocked_checks"] or 0
            )

            block_rate_percent = (
                round(
                    (
                        blocked_checks
                        / total_checks
                    ) * 100,
                    2,
                )
                if total_checks > 0
                else 0.0
            )

            result.append(
                {
                    "policy_id": (
                        row["policy_id"]
                    ),

                    "project_id": (
                        row["project_id"]
                    ),

                    "route_path": (
                        row["route_path"]
                    ),

                    "http_method": (
                        row["http_method"]
                    ),

                    "capacity": (
                        row["capacity"]
                    ),

                    "refill_amount": float(
                        row["refill_amount"]
                    ),

                    "refill_unit": (
                        row["refill_unit"]
                    ),

                    "is_active": (
                        row["is_active"]
                    ),

                    "total_checks": (
                        total_checks
                    ),

                    "allowed_checks": (
                        allowed_checks
                    ),

                    "blocked_checks": (
                        blocked_checks
                    ),

                    "block_rate_percent": (
                        block_rate_percent
                    ),

                    "unique_subjects": int(
                        row[
                            "unique_subjects"
                        ] or 0
                    ),

                    "average_latency_ms": round(
                        float(
                            row[
                                "average_latency_ms"
                            ] or 0.0
                        ),
                        2,
                    ),

                    "last_request_at": (
                        row[
                            "last_request_at"
                        ]
                    ),
                }
            )

        return result