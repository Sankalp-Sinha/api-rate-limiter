from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class RateLimitPolicy(Base):
    __tablename__ = "rate_limit_policies"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "plan_id",
            "route_path",
            "http_method",
            name="uq_policy_project_plan_route_method",
        ),

        CheckConstraint(
            "capacity > 0",
            name="ck_policy_capacity_positive",
        ),

        CheckConstraint(
            "refill_rate > 0",
            name="ck_policy_refill_rate_positive",
        ),

        CheckConstraint(
            "refill_amount > 0",
            name="ck_policy_refill_amount_positive",
        ),

        CheckConstraint(
            "tokens_required > 0",
            name="ck_policy_tokens_required_positive",
        ),

        CheckConstraint(
            "refill_unit IN ('second', 'minute', 'hour')",
            name="ck_policy_refill_unit_valid",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    project_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    plan_id: Mapped[int] = mapped_column(
        ForeignKey(
            "plans.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    route_path: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    http_method: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Internal normalized value:
    # tokens added per second.
    refill_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # Developer-facing value.
    refill_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        server_default="1",
    )

    # second | minute | hour
    refill_unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="second",
        server_default="second",
    )

    tokens_required: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )