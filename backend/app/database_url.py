def normalize_database_url(
    database_url: str,
) -> str:
    url = database_url.strip()

    if url.startswith(
        "postgresql+psycopg://"
    ):
        return url

    if url.startswith(
        "postgresql://"
    ):
        return (
            "postgresql+psycopg://"
            + url[
                len("postgresql://"):
            ]
        )

    if url.startswith(
        "postgres://"
    ):
        return (
            "postgresql+psycopg://"
            + url[
                len("postgres://"):
            ]
        )

    return url