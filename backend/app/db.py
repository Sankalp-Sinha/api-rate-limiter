import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
)

from app.database_url import (
    normalize_database_url,
)


load_dotenv()


RAW_DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


if not RAW_DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment "
        "variable is not configured"
    )


RAW_DATABASE_URL = (
    RAW_DATABASE_URL.strip()
)


DATABASE_URL = normalize_database_url(
    RAW_DATABASE_URL
)


if not DATABASE_URL.startswith(
    (
        "postgresql+psycopg://",
        "postgresql://",
        "postgres://",
    )
):
    raise RuntimeError(
        "DATABASE_URL has an invalid format. "
        f"Received prefix: "
        f"{DATABASE_URL[:30]!r}"
    )


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)