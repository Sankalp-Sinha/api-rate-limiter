from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    __table_args__ = (
        Index(
            "ix_request_logs_route_created",
            "route_path",
            "created_at",
        ),
        Index(
            "ix_request_logs_api_key_created",
            "api_key_id",
            "created_at",
        ),
        Index(
            "ix_request_logs_decision_created",
            "decision",
            "created_at",
        ),
        Index(
            "ix_request_logs_project_policy_created",
            "project_id",
            "policy_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    request_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
    )

    api_key_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "api_keys.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    project_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    policy_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "rate_limit_policies.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # Hash of user:42 / ip:... / org:...
    # We do not store the raw subject.
    subject_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    plan_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    route_path: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    http_method: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    remaining_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    retry_after_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )