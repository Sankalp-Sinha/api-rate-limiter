from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()


def hash_password(
    raw_password: str,
) -> str:
    return password_hasher.hash(
        raw_password
    )


def verify_password(
    raw_password: str,
    hashed_password: str,
) -> bool:
    return password_hasher.verify(
        raw_password,
        hashed_password,
    )