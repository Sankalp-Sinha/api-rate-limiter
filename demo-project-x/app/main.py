import os

import httpx
from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    status,
)


load_dotenv()


RATEGUARD_BASE_URL = os.getenv(
    "RATEGUARD_BASE_URL",
    "http://127.0.0.1:8000",
)

RATEGUARD_API_KEY = os.getenv(
    "RATEGUARD_API_KEY"
)


if not RATEGUARD_API_KEY:
    raise RuntimeError(
        "RATEGUARD_API_KEY is not configured"
    )


app = FastAPI(
    title="Demo Project X",
    description=(
        "A separate demo application "
        "integrated with RateGuard"
    ),
    version="1.0.0",
)


async def check_rateguard(
    *,
    subject: str,
    route: str,
    method: str,
) -> dict:
    """
    Ask RateGuard whether this request
    should be allowed.
    """

    async with httpx.AsyncClient(
        timeout=5.0
    ) as client:
        response = await client.post(
            f"{RATEGUARD_BASE_URL}/v1/check",
            headers={
                "Authorization": (
                    f"Bearer "
                    f"{RATEGUARD_API_KEY}"
                )
            },
            json={
                "subject": subject,
                "route": route,
                "method": method,
            },
        )

    if response.status_code == 401:
        raise HTTPException(
            status_code=500,
            detail=(
                "Project X has an invalid "
                "RateGuard integration key"
            ),
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=500,
            detail=(
                "No RateGuard policy is "
                "configured for this endpoint"
            ),
        )

    if response.status_code >= 500:
        raise HTTPException(
            status_code=503,
            detail=(
                "RateGuard is temporarily "
                "unavailable"
            ),
        )

    if not response.is_success:
        raise HTTPException(
            status_code=502,
            detail=(
                "Unexpected response "
                "from RateGuard"
            ),
        )

    return response.json()


@app.get("/")
def health():
    return {
        "service": "Demo Project X",
        "status": "running",
    }


@app.post("/generate-resume")
async def generate_resume(
    x_user_id: str = Header(
        alias="x-user-id"
    ),
):
    subject = f"user:{x_user_id}"

    decision = await check_rateguard(
        subject=subject,
        route="/generate-resume",
        method="POST",
    )

    if not decision["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": (
                    "Too many resume "
                    "generation requests"
                ),
                "remaining": (
                    decision["remaining"]
                ),
                "retry_after_seconds": (
                    decision[
                        "retry_after_seconds"
                    ]
                ),
            },
        )

    # This represents Project X's
    # actual business logic.
    generated_resume = {
        "summary": (
            "Software engineer with "
            "experience building scalable "
            "backend systems."
        ),
        "skills": [
            "Python",
            "FastAPI",
            "Redis",
            "PostgreSQL",
        ],
    }

    return {
        "success": True,
        "message": "Resume generated",
        "resume": generated_resume,

        # Useful only for this demo.
        "rate_limit": {
            "limit": decision["limit"],
            "remaining": (
                decision["remaining"]
            ),
            "reset_after_seconds": (
                decision[
                    "reset_after_seconds"
                ]
            ),
        },
    }