from sqlalchemy import select

from app.db import SessionLocal
from app.models.plan import Plan
from app.models.project import Project
from app.models.rate_limit_policy import (
    RateLimitPolicy,
)


UNIT_SECONDS = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
}


def normalize_route_path(
    route_path: str,
) -> str:
    path = route_path.strip()

    if not path.startswith("/"):
        path = "/" + path

    if len(path) > 1:
        path = path.rstrip("/")

    return path


def calculate_refill_rate(
    refill_amount: float,
    refill_unit: str,
) -> float:
    seconds = UNIT_SECONDS[
        refill_unit
    ]

    return refill_amount / seconds


def policy_to_dict(
    policy: RateLimitPolicy,
) -> dict:
    return {
        "id": policy.id,
        "project_id": (
            policy.project_id
        ),
        "route_path": (
            policy.route_path
        ),
        "http_method": (
            policy.http_method
        ),
        "capacity": (
            policy.capacity
        ),
        "refill_rate": (
            policy.refill_rate
        ),
        "refill_amount": (
            policy.refill_amount
        ),
        "refill_unit": (
            policy.refill_unit
        ),
        "tokens_required": (
            policy.tokens_required
        ),
        "is_active": (
            policy.is_active
        ),
        "created_at": (
            policy.created_at
        ),
    }


def create_project_policy(
    *,
    project_id: int,
    owner_id: int,
    route_path: str,
    http_method: str,
    capacity: int,
    refill_amount: float,
    refill_unit: str,
    tokens_required: int,
) -> tuple[str, dict | None]:
    with SessionLocal() as db:
        project = db.scalar(
            select(Project).where(
                Project.id == project_id,
                Project.owner_id
                == owner_id,
                Project.is_active.is_(True),
            )
        )

        if project is None:
            return (
                "project_not_found",
                None,
            )

        free_plan = db.scalar(
            select(Plan).where(
                Plan.name == "free",
                Plan.is_active.is_(True),
            )
        )

        if free_plan is None:
            return (
                "free_plan_not_found",
                None,
            )

        normalized_path = (
            normalize_route_path(
                route_path
            )
        )

        normalized_method = (
            http_method.upper()
        )

        existing = db.scalar(
            select(
                RateLimitPolicy
            ).where(
                RateLimitPolicy.project_id
                == project_id,

                RateLimitPolicy.plan_id
                == free_plan.id,

                RateLimitPolicy.route_path
                == normalized_path,

                RateLimitPolicy.http_method
                == normalized_method,
            )
        )

        if existing is not None:
            return (
                "duplicate",
                None,
            )

        refill_rate = (
            calculate_refill_rate(
                refill_amount=refill_amount,
                refill_unit=refill_unit,
            )
        )

        policy = RateLimitPolicy(
            project_id=project_id,
            plan_id=free_plan.id,
            route_path=normalized_path,
            http_method=normalized_method,
            capacity=capacity,
            refill_rate=refill_rate,
            refill_amount=refill_amount,
            refill_unit=refill_unit,
            tokens_required=tokens_required,
            is_active=True,
        )

        db.add(policy)
        db.commit()
        db.refresh(policy)

        return (
            "ok",
            policy_to_dict(policy),
        )


def list_project_policies(
    *,
    project_id: int,
    owner_id: int,
) -> list[dict] | None:
    with SessionLocal() as db:
        project = db.scalar(
            select(Project).where(
                Project.id == project_id,
                Project.owner_id
                == owner_id,
            )
        )

        if project is None:
            return None

        policies = db.scalars(
            select(RateLimitPolicy)
            .where(
                RateLimitPolicy.project_id
                == project_id
            )
            .order_by(
                RateLimitPolicy
                .created_at
                .desc()
            )
        ).all()

        return [
            policy_to_dict(policy)
            for policy in policies
        ]


def update_project_policy(
    *,
    project_id: int,
    policy_id: int,
    owner_id: int,
    capacity: int,
    refill_amount: float,
    refill_unit: str,
    tokens_required: int,
) -> dict | None:
    with SessionLocal() as db:
        policy = db.scalar(
            select(RateLimitPolicy)
            .join(
                Project,
                RateLimitPolicy.project_id
                == Project.id,
            )
            .where(
                RateLimitPolicy.id
                == policy_id,

                RateLimitPolicy.project_id
                == project_id,

                Project.owner_id
                == owner_id,
            )
        )

        if policy is None:
            return None

        policy.capacity = capacity

        policy.refill_amount = (
            refill_amount
        )

        policy.refill_unit = (
            refill_unit
        )

        policy.refill_rate = (
            calculate_refill_rate(
                refill_amount=refill_amount,
                refill_unit=refill_unit,
            )
        )

        policy.tokens_required = (
            tokens_required
        )

        db.commit()
        db.refresh(policy)

        return policy_to_dict(policy)


def deactivate_project_policy(
    *,
    project_id: int,
    policy_id: int,
    owner_id: int,
) -> dict | None:
    with SessionLocal() as db:
        policy = db.scalar(
            select(RateLimitPolicy)
            .join(
                Project,
                RateLimitPolicy.project_id
                == Project.id,
            )
            .where(
                RateLimitPolicy.id
                == policy_id,

                RateLimitPolicy.project_id
                == project_id,

                Project.owner_id
                == owner_id,
            )
        )

        if policy is None:
            return None

        policy.is_active = False

        db.commit()
        db.refresh(policy)

        return policy_to_dict(policy)