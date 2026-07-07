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


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()