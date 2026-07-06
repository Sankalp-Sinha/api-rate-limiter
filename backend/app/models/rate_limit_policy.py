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
            "plan_id",
            "route_path",
            "http_method",
            name="uq_policy_plan_route_method"
        ),
        CheckConstraint(
            "capacity > 0",
            name="ck_policy_capacity_positive"
        ),
        CheckConstraint(
            "refill_rate > 0",
            name="ck_policy_refill_rate_positive"
        ),
        CheckConstraint(
            "tokens_required > 0",
            name="ck_policy_tokens_required_positive"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    plan_id: Mapped[int] = mapped_column(
        ForeignKey(
            "plans.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    route_path: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    http_method: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    refill_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    tokens_required: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )