from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.dependencies.current_user import (
    get_current_user,
)
from app.models.user import User
from app.schemas.auth import (
    AuthTokenResponse,
    AuthUserResponse,
    LoginRequest,
    RegisterRequest,
)
from app.services.auth_service import (
    authenticate_user,
    create_user,
)
from app.services.jwt_service import (
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
):
    result_status, user = create_user(
        name=payload.name,
        email=str(payload.email),
        password=payload.password,
    )

    if result_status == "email_exists":
        raise HTTPException(
            status_code=409,
            detail=(
                "An account with this "
                "email already exists"
            ),
        )

    if user is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not create account"
            ),
        )

    token, expires_in = (
        create_access_token(
            user_id=user.id
        )
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": user,
    }


@router.post(
    "/login",
    response_model=AuthTokenResponse,
)
def login(
    payload: LoginRequest,
):
    user = authenticate_user(
        email=str(payload.email),
        password=payload.password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid email or password"
            ),
        )

    token, expires_in = (
        create_access_token(
            user_id=user.id
        )
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": user,
    }


@router.get(
    "/me",
    response_model=AuthUserResponse,
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return current_user