import hashlib
from dataclasses import dataclass

from sqlalchemy import func, or_, select

from app.db import SessionLocal
from app.models import ApiKey, Plan, RateLimitPolicy


@dataclass(frozen=True)
class RateLimitContext:
    api_key_id: int
    plan_name: str
    capacity: int
    refill_rate: float
    tokens_required: int


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(
        api_key.encode("utf-8")
    ).hexdigest()


def get_rate_limit_context(
    raw_api_key: str,
    route_path: str,
    http_method: str
) -> tuple[str, RateLimitContext | None]:

    api_key_hash = hash_api_key(raw_api_key)

    with SessionLocal() as db:
        auth_statement = (
            select(
                ApiKey.id,
                ApiKey.plan_id,
                Plan.name
            )
            .join(
                Plan,
                Plan.id == ApiKey.plan_id
            )
            .where(
                ApiKey.key_hash == api_key_hash,
                ApiKey.is_active.is_(True),
                Plan.is_active.is_(True),
                or_(
                    ApiKey.expires_at.is_(None),
                    ApiKey.expires_at > func.now()
                )
            )
        )

        auth_result = db.execute(
            auth_statement
        ).one_or_none()

        if auth_result is None:
            return "invalid_key", None

        policy_statement = (
            select(
                RateLimitPolicy.capacity,
                RateLimitPolicy.refill_rate,
                RateLimitPolicy.tokens_required
            )
            .where(
                RateLimitPolicy.plan_id == auth_result.plan_id,
                RateLimitPolicy.route_path == route_path,
                RateLimitPolicy.http_method == http_method.upper(),
                RateLimitPolicy.is_active.is_(True)
            )
        )

        policy_result = db.execute(
            policy_statement
        ).one_or_none()

        if policy_result is None:
            return "no_policy", None

        context = RateLimitContext(
            api_key_id=auth_result.id,
            plan_name=auth_result.name,
            capacity=policy_result.capacity,
            refill_rate=policy_result.refill_rate,
            tokens_required=policy_result.tokens_required
        )

        return "ok", context