import hashlib


def hash_subject(
    subject: str,
) -> str:
    normalized = subject.strip()

    return hashlib.sha256(
        normalized.encode("utf-8")
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