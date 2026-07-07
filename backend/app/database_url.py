def normalize_database_url(
    database_url: str,
) -> str:
    """
    Ensure SQLAlchemy uses psycopg 3
    for PostgreSQL connections.
    """

    if database_url.startswith(
        "postgresql://"
    ):
        return (
            "postgresql+psycopg://"
            + database_url[
                len("postgresql://"):
            ]
        )

    if database_url.startswith(
        "postgres://"
    ):
        return (
            "postgresql+psycopg://"
            + database_url[
                len("postgres://"):
            ]
        )

    return database_url