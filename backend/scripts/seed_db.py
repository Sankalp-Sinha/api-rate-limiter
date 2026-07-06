from sqlalchemy import select

from app.db import SessionLocal
from app.models import ApiKey, Plan, RateLimitPolicy
from app.services.api_key_service import hash_api_key


FREE_API_KEY = "free_key_123"
PRO_API_KEY = "pro_key_456"


def get_or_create_plan(
    db,
    name: str,
    description: str
) -> Plan:

    plan = db.scalar(
        select(Plan).where(
            Plan.name == name
        )
    )

    if plan is None:
        plan = Plan(
            name=name,
            description=description,
            is_active=True
        )
        db.add(plan)
        db.flush()
    else:
        plan.description = description
        plan.is_active = True

    return plan


def upsert_api_key(
    db,
    name: str,
    raw_key: str,
    plan_id: int
) -> None:

    key_hash = hash_api_key(raw_key)

    api_key = db.scalar(
        select(ApiKey).where(
            ApiKey.key_hash == key_hash
        )
    )

    if api_key is None:
        api_key = ApiKey(
            name=name,
            key_prefix=raw_key[:4],
            key_hash=key_hash,
            plan_id=plan_id,
            is_active=True
        )
        db.add(api_key)
    else:
        api_key.name = name
        api_key.plan_id = plan_id
        api_key.is_active = True


def upsert_policy(
    db,
    plan_id: int,
    route_path: str,
    http_method: str,
    capacity: int,
    refill_rate: float,
    tokens_required: int
) -> None:

    policy = db.scalar(
        select(RateLimitPolicy).where(
            RateLimitPolicy.plan_id == plan_id,
            RateLimitPolicy.route_path == route_path,
            RateLimitPolicy.http_method == http_method
        )
    )

    if policy is None:
        policy = RateLimitPolicy(
            plan_id=plan_id,
            route_path=route_path,
            http_method=http_method,
            capacity=capacity,
            refill_rate=refill_rate,
            tokens_required=tokens_required,
            is_active=True
        )
        db.add(policy)
    else:
        policy.capacity = capacity
        policy.refill_rate = refill_rate
        policy.tokens_required = tokens_required
        policy.is_active = True


def seed_database() -> None:
    with SessionLocal() as db:
        try:
            free_plan = get_or_create_plan(
                db,
                name="free",
                description="Free developer plan"
            )

            pro_plan = get_or_create_plan(
                db,
                name="pro",
                description="Pro developer plan"
            )

            upsert_api_key(
                db,
                name="Free Demo Client",
                raw_key=FREE_API_KEY,
                plan_id=free_plan.id
            )

            upsert_api_key(
                db,
                name="Pro Demo Client",
                raw_key=PRO_API_KEY,
                plan_id=pro_plan.id
            )

            upsert_policy(
                db,
                plan_id=free_plan.id,
                route_path="/api/protected",
                http_method="GET",
                capacity=5,
                refill_rate=1,
                tokens_required=1
            )

            upsert_policy(
                db,
                plan_id=pro_plan.id,
                route_path="/api/protected",
                http_method="GET",
                capacity=20,
                refill_rate=5,
                tokens_required=1
            )

            db.commit()

            print("Database seeded successfully.")
            print(f"Free demo key: {FREE_API_KEY}")
            print(f"Pro demo key: {PRO_API_KEY}")

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed_database()