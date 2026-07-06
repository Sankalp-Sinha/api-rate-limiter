import os
from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt
from jwt.exceptions import InvalidTokenError


JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        "480",
    )
)


if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is not configured"
    )


def create_access_token(
    user_id: int,
) -> tuple[str, int]:
    now = datetime.now(
        timezone.utc
    )

    expires_at = now + timedelta(
        minutes=(
            ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    expires_in_seconds = (
        ACCESS_TOKEN_EXPIRE_MINUTES
        * 60
    )

    return (
        token,
        expires_in_seconds,
    )


def decode_access_token(
    token: str,
) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[
                JWT_ALGORITHM
            ],
        )

        if (
            payload.get("type")
            != "access"
        ):
            return None

        if not payload.get("sub"):
            return None

        return payload

    except InvalidTokenError:
        return None