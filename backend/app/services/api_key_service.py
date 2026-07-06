import hashlib
from dataclasses import dataclass

from sqlalchemy import (
    func,
    or_,
    select,
)

from app.db import SessionLocal
from app.models.api_key import ApiKey
from app.models.plan import Plan
from app.models.rate_limit_policy import (
    RateLimitPolicy,
)


def hash_api_key(
    raw_api_key: str,
) -> str:
    return hashlib.sha256(
        raw_api_key.encode("utf-8")
    ).hexdigest()


@dataclass
class RateLimitContext:
    api_key_id: int
    project_id: int | None
    policy_id: int
    plan_name: str
    capacity: int
    refill_rate: float
    tokens_required: int


def get_rate_limit_context(
    raw_api_key: str,
    route_path: str,
    http_method: str,
) -> tuple[
    str,
    RateLimitContext | None,
]:
    key_hash = hash_api_key(
        raw_api_key
    )

    with SessionLocal() as db:
        row = db.execute(
            select(
                ApiKey,
                Plan,
            )
            .join(
                Plan,
                ApiKey.plan_id == Plan.id,
            )
            .where(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active.is_(True),
                Plan.is_active.is_(True),

                or_(
                    ApiKey.expires_at.is_(None),
                    ApiKey.expires_at
                    > func.now(),
                ),
            )
        ).first()

        if row is None:
            return "invalid_key", None

        api_key, plan = row

        if api_key.project_id is None:
            project_condition = (
                RateLimitPolicy.project_id
                .is_(None)
            )
        else:
            project_condition = (
                RateLimitPolicy.project_id
                == api_key.project_id
            )

        policy = db.scalar(
            select(RateLimitPolicy).where(
                RateLimitPolicy.plan_id
                == plan.id,

                project_condition,

                RateLimitPolicy.route_path
                == route_path,

                RateLimitPolicy.http_method
                == http_method.upper(),

                RateLimitPolicy.is_active
                .is_(True),
            )
        )

        if policy is None:
            return "no_policy", None

        return (
            "ok",
            RateLimitContext(
                api_key_id=api_key.id,
                project_id=(
                    api_key.project_id
                ),
                policy_id=policy.id,
                plan_name=plan.name,
                capacity=policy.capacity,
                refill_rate=(
                    policy.refill_rate
                ),
                tokens_required=(
                    policy.tokens_required
                ),
            ),
        )