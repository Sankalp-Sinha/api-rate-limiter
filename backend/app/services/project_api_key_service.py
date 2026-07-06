import secrets

from sqlalchemy import select

from app.db import SessionLocal
from app.models.api_key import ApiKey
from app.models.plan import Plan
from app.models.project import Project
from app.services.api_key_service import hash_api_key


def generate_project_api_key() -> str:
    """
    Generate a secret key representing one
    RateGuard project integration.
    """

    return (
        "rg_project_"
        + secrets.token_urlsafe(32)
    )


def create_project_api_key(
    project_id: int,
    name: str,
) -> dict | None:
    with SessionLocal() as db:
        project = db.scalar(
            select(Project).where(
                Project.id == project_id,
                Project.is_active.is_(True),
            )
        )

        if project is None:
            return None

        # For now RateGuard has only one plan:
        # the Free plan.
        free_plan = db.scalar(
            select(Plan).where(
                Plan.name == "free",
                Plan.is_active.is_(True),
            )
        )

        if free_plan is None:
            raise RuntimeError(
                "Active free plan not found. "
                "Run the database seed script."
            )

        raw_api_key = generate_project_api_key()

        api_key = ApiKey(
            project_id=project_id,
            plan_id=free_plan.id,
            name=name.strip(),
            key_prefix=raw_api_key[:16],
            key_hash=hash_api_key(
                raw_api_key
            ),
            is_active=True,
            expires_at=None,
        )

        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        return {
            "id": api_key.id,
            "project_id": project_id,
            "name": api_key.name,
            "api_key": raw_api_key,
            "key_prefix": api_key.key_prefix,
            "is_active": api_key.is_active,
            "expires_at": api_key.expires_at,
            "created_at": api_key.created_at,
            "message": (
                "Copy this API key now. "
                "It will not be shown again."
            ),
        }


def list_project_api_keys(
    project_id: int,
) -> list[ApiKey]:
    with SessionLocal() as db:
        api_keys = db.scalars(
            select(ApiKey)
            .where(
                ApiKey.project_id == project_id
            )
            .order_by(
                ApiKey.created_at.desc()
            )
        ).all()

        return list(api_keys)


def revoke_project_api_key(
    project_id: int,
    api_key_id: int,
) -> ApiKey | None:
    with SessionLocal() as db:
        api_key = db.scalar(
            select(ApiKey).where(
                ApiKey.id == api_key_id,
                ApiKey.project_id == project_id,
            )
        )

        if api_key is None:
            return None

        api_key.is_active = False

        db.commit()
        db.refresh(api_key)

        return api_key