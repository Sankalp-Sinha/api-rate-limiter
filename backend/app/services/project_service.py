import re
from uuid import uuid4

from sqlalchemy import select

from app.db import SessionLocal
from app.models.project import Project


def make_slug(name: str) -> str:
    """
    Convert:
        AI Resume Generator
    into:
        ai-resume-generator
    """

    slug = name.strip().lower()

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        slug
    )

    slug = slug.strip("-")

    return slug


def create_project(
    name: str
) -> Project:
    with SessionLocal() as db:
        base_slug = make_slug(name)

        if not base_slug:
            base_slug = "project"

        slug = base_slug

        existing = db.scalar(
            select(Project).where(
                Project.slug == slug
            )
        )

        if existing:
            short_id = uuid4().hex[:8]

            slug = (
                f"{base_slug}-{short_id}"
            )

        project = Project(
            name=name.strip(),
            slug=slug,
            is_active=True,
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project


def list_projects() -> list[Project]:
    with SessionLocal() as db:
        projects = db.scalars(
            select(Project)
            .order_by(
                Project.created_at.desc()
            )
        ).all()

        return list(projects)


def get_project(
    project_id: int
) -> Project | None:
    with SessionLocal() as db:
        return db.scalar(
            select(Project).where(
                Project.id == project_id
            )
        )