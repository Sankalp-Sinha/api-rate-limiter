"""add project ownership

Revision ID: 506b354a4dac
Revises: 6113be0ff300
Create Date: 2026-07-07 10:10:35.532926

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '506b354a4dac'
down_revision: Union[str, Sequence[str], None] = '6113be0ff300'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1:
    # Add owner_id temporarily as nullable
    # because old projects already exist.
    op.add_column(
        "projects",
        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Step 2:
    # Add index.
    op.create_index(
        "ix_projects_owner_id",
        "projects",
        ["owner_id"],
        unique=False,
    )

    # Step 3:
    # Add foreign key.
    op.create_foreign_key(
        "fk_projects_owner_id_users",
        "projects",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )

    connection = op.get_bind()

    # Existing project count.
    existing_project_count = (
        connection.execute(
            sa.text(
                "SELECT COUNT(*) "
                "FROM projects"
            )
        ).scalar_one()
    )

    # For our existing local development data,
    # assign old projects to the earliest
    # registered developer.
    legacy_owner_id = (
        connection.execute(
            sa.text(
                "SELECT id "
                "FROM users "
                "ORDER BY id "
                "LIMIT 1"
            )
        ).scalar_one_or_none()
    )

    if (
        existing_project_count > 0
        and legacy_owner_id is None
    ):
        raise RuntimeError(
            "Cannot backfill existing projects: "
            "no developer user exists."
        )

    if legacy_owner_id is not None:
        connection.execute(
            sa.text(
                "UPDATE projects "
                "SET owner_id = :owner_id "
                "WHERE owner_id IS NULL"
            ),
            {
                "owner_id": legacy_owner_id
            },
        )

    # Step 4:
    # After all old projects have owners,
    # enforce NOT NULL.
    op.alter_column(
        "projects",
        "owner_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_projects_owner_id_users",
        "projects",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_projects_owner_id",
        table_name="projects",
    )

    op.drop_column(
        "projects",
        "owner_id",
    )
