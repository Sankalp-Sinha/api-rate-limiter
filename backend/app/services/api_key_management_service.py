import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ApiKey, Plan
from app.services.api_key_service import hash_api_key


def generate_raw_api_key() -> str:
    random_part = secrets.token_urlsafe(32)

    return f"rl_live_{random_part}"


def create_api_key(
    db: Session,
    name: str,
    plan_id: int,
    expires_in_days: int | None
) -> dict | None:

    plan = db.scalar(
        select(Plan).where(
            Plan.id == plan_id,
            Plan.is_active.is_(True)
        )
    )

    if plan is None:
        return None

    raw_api_key = generate_raw_api_key()
    api_key_hash = hash_api_key(raw_api_key)

    expires_at = None

    if expires_in_days is not None:
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=expires_in_days)
        )

    api_key = ApiKey(
        name=name,
        key_prefix=raw_api_key[:16],
        key_hash=api_key_hash,
        plan_id=plan.id,
        is_active=True,
        expires_at=expires_at
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {
        "id": api_key.id,
        "name": api_key.name,
        "api_key": raw_api_key,
        "key_prefix": api_key.key_prefix,
        "plan_name": plan.name,
        "expires_at": api_key.expires_at,
        "message": (
            "Store this API key securely. "
            "It will not be shown again."
        )
    }


def list_api_keys(
    db: Session
) -> list[dict]:

    statement = (
        select(
            ApiKey,
            Plan.name
        )
        .join(
            Plan,
            Plan.id == ApiKey.plan_id
        )
        .order_by(
            ApiKey.created_at.desc()
        )
    )

    rows = db.execute(statement).all()

    return [
        {
            "id": api_key.id,
            "name": api_key.name,
            "key_prefix": api_key.key_prefix,
            "plan_name": plan_name,
            "is_active": api_key.is_active,
            "expires_at": api_key.expires_at,
            "created_at": api_key.created_at
        }
        for api_key, plan_name in rows
    ]


def revoke_api_key(
    db: Session,
    api_key_id: int
) -> bool:

    api_key = db.get(
        ApiKey,
        api_key_id
    )

    if api_key is None:
        return False

    api_key.is_active = False

    db.commit()

    return True


def list_plans(
    db: Session
) -> list[dict]:

    plans = db.scalars(
        select(Plan).order_by(
            Plan.id
        )
    ).all()

    return [
        {
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "is_active": plan.is_active
        }
        for plan in plans
    ]