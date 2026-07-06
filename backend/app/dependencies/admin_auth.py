import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import (
    Depends,
    Header,
    HTTPException,
)
from app.dependencies.current_user import (
    get_current_user,
)
from app.models.user import User


BACKEND_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

load_dotenv(
    BACKEND_DIR / ".env",
    override=True,
)


ADMIN_API_KEY = os.getenv(
    "ADMIN_API_KEY"
)


def require_admin(
    x_admin_key: str | None = Header(
        default=None,
        alias="x-admin-key",
    ),
    current_user: User = Depends(
        get_current_user
    ),
) -> User:
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "Admin authentication "
                "is not configured"
            ),
        )

    if x_admin_key is None:
        raise HTTPException(
            status_code=401,
            detail="Missing admin key",
        )

    if not secrets.compare_digest(
        x_admin_key,
        ADMIN_API_KEY,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin key",
        )

    return current_user