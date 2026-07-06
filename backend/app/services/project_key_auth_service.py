from dataclasses import dataclass

from sqlalchemy import (
    func,
    or_,
    select,
)

from app.db import SessionLocal
from app.models.api_key import ApiKey
from app.models.plan import Plan
from app.models.project import Project
from app.services.api_key_service import (
    hash_api_key,
)


@dataclass
class ProjectKeyContext:
    api_key_id: int

    project_id: int
    project_name: str

    plan_id: int
    plan_name: str


def authenticate_project_key(
    raw_api_key: str,
) -> ProjectKeyContext | None:
    key_hash = hash_api_key(
        raw_api_key
    )

    with SessionLocal() as db:
        row = db.execute(
            select(
                ApiKey,
                Project,
                Plan,
            )
            .join(
                Project,
                ApiKey.project_id
                == Project.id,
            )
            .join(
                Plan,
                ApiKey.plan_id
                == Plan.id,
            )
            .where(
                ApiKey.key_hash
                == key_hash,

                ApiKey.is_active
                .is_(True),

                Project.is_active
                .is_(True),

                Plan.is_active
                .is_(True),

                or_(
                    ApiKey.expires_at
                    .is_(None),

                    ApiKey.expires_at
                    > func.now(),
                ),
            )
        ).first()

        if row is None:
            return None

        api_key, project, plan = row

        return ProjectKeyContext(
            api_key_id=api_key.id,
            project_id=project.id,
            project_name=project.name,
            plan_id=plan.id,
            plan_name=plan.name,
        )