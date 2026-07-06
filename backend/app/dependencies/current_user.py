from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.models.user import User
from app.services.auth_service import (
    get_user_by_id,
)
from app.services.jwt_service import (
    decode_access_token,
)


bearer_scheme = HTTPBearer(
    auto_error=False
)


async def get_current_user(
    credentials: (
        HTTPAuthorizationCredentials
        | None
    ) = Depends(bearer_scheme),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Authentication required",
        )

    if (
        credentials.scheme.lower()
        != "bearer"
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme",
        )

    payload = decode_access_token(
        credentials.credentials
    )

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid or expired "
                "access token"
            ),
        )

    try:
        user_id = int(
            payload["sub"]
        )
    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid access token",
        )

    user = get_user_by_id(
        user_id=user_id
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail=(
                "User not found "
                "or inactive"
            ),
        )

    return user