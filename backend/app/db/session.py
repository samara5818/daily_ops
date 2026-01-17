import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./daily_ops.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    # Ensure models are imported before creating tables.
    from app.models.user import User  # noqa: F401
    from app.models.user_profile import UserProfile  # noqa: F401
    from app.models.day_override import DayOverride  # noqa: F401
    from app.models.plan import Plan  # noqa: F401
    from app.models.health_profile import HealthProfile  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
