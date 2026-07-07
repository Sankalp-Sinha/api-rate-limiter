import hashlib
import hmac
import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

load_dotenv(
    BACKEND_DIR / ".env",
    override=False,
)


SUBJECT_HASH_SECRET = os.getenv(
    "SUBJECT_HASH_SECRET"
)


if not SUBJECT_HASH_SECRET:
    raise RuntimeError(
        "SUBJECT_HASH_SECRET "
        "is not configured"
    )


def hash_subject(
    *,
    project_id: int,
    subject: str,
) -> str:
    """
    Create a stable, project-scoped,
    pseudonymous subject identifier.

    Raw subjects are never stored.
    """

    normalized_subject = (
        subject.strip()
    )

    message = (
        f"{project_id}:"
        f"{normalized_subject}"
    ).encode("utf-8")

    return hmac.new(
        key=SUBJECT_HASH_SECRET.encode(
            "utf-8"
        ),
        msg=message,
        digestmod=hashlib.sha256,
    ).hexdigest()


def build_subject_bucket_key(
    project_id: int,
    policy_id: int,
    subject_hash: str,
) -> str:
    return (
        "rate_limit:"
        f"project:{project_id}:"
        f"policy:{policy_id}:"
        f"subject:{subject_hash}"
    )