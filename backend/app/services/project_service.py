import re
from uuid import uuid4

from sqlalchemy import select

from app.db import SessionLocal
from app.models.project import Project


def make_slug(
    name: str,
) -> str:
    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        name.strip().lower(),
    )

    slug = slug.strip("-")

    return slug or "project"


def create_project(
    *,
    name: str,
    owner_id: int,
) -> Project:
    with SessionLocal() as db:
        base_slug = make_slug(name)

        slug = base_slug

        existing = db.scalar(
            select(Project).where(
                Project.slug == slug
            )
        )

        if existing is not None:
            slug = (
                f"{base_slug}-"
                f"{uuid4().hex[:8]}"
            )

        project = Project(
            owner_id=owner_id,
            name=name.strip(),
            slug=slug,
            is_active=True,
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project


def list_projects(
    *,
    owner_id: int,
) -> list[Project]:
    with SessionLocal() as db:
        projects = db.scalars(
            select(Project)
            .where(
                Project.owner_id
                == owner_id
            )
            .order_by(
                Project.created_at.desc()
            )
        ).all()

        return list(projects)


def get_project(
    *,
    project_id: int,
    owner_id: int,
) -> Project | None:
    with SessionLocal() as db:
        return db.scalar(
            select(Project).where(
                Project.id == project_id,
                Project.owner_id
                == owner_id,
            )
        )