from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.models.user import User
from app.services.password_service import (
    hash_password,
    verify_password,
)


def normalize_email(
    email: str,
) -> str:
    return email.strip().lower()


def create_user(
    *,
    name: str,
    email: str,
    password: str,
) -> tuple[str, User | None]:
    normalized_email = normalize_email(
        email
    )

    with SessionLocal() as db:
        existing = db.scalar(
            select(User).where(
                User.email
                == normalized_email
            )
        )

        if existing is not None:
            return (
                "email_exists",
                None,
            )

        user = User(
            name=name.strip(),
            email=normalized_email,
            password_hash=hash_password(
                password
            ),
            is_active=True,
        )

        db.add(user)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()

            return (
                "email_exists",
                None,
            )

        db.refresh(user)

        return (
            "ok",
            user,
        )


def authenticate_user(
    *,
    email: str,
    password: str,
) -> User | None:
    normalized_email = normalize_email(
        email
    )

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(
                User.email
                == normalized_email,

                User.is_active
                .is_(True),
            )
        )

        if user is None:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user


def get_user_by_id(
    user_id: int,
) -> User | None:
    with SessionLocal() as db:
        return db.scalar(
            select(User).where(
                User.id == user_id,
                User.is_active.is_(True),
            )
        )