import os
import secrets
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Header, HTTPException, status


BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(
    dotenv_path=BACKEND_DIR / ".env",
    override=True
)


ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

if not ADMIN_API_KEY:
    raise RuntimeError(
        "ADMIN_API_KEY environment variable is not configured"
    )


def require_admin(
    x_admin_key: Annotated[
        str | None,
        Header(alias="x-admin-key")
    ] = None
) -> None:

    if not x_admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin API key"
        )

    if not secrets.compare_digest(
        x_admin_key,
        ADMIN_API_KEY
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key"
        )