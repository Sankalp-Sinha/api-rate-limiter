from sqlalchemy import select

from app.db import SessionLocal
from app.models.rate_limit_policy import (
    RateLimitPolicy,
)
from app.services.project_policy_service import (
    normalize_route_path,
)


def get_active_project_policy(
    project_id: int,
    plan_id: int,
    route_path: str,
    http_method: str,
) -> RateLimitPolicy | None:
    normalized_path = normalize_route_path(
        route_path
    )

    normalized_method = (
        http_method.upper()
    )

    with SessionLocal() as db:
        return db.scalar(
            select(RateLimitPolicy).where(
                RateLimitPolicy.project_id
                == project_id,

                RateLimitPolicy.plan_id
                == plan_id,

                RateLimitPolicy.route_path
                == normalized_path,

                RateLimitPolicy.http_method
                == normalized_method,

                RateLimitPolicy.is_active
                .is_(True),
            )
        )