from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, JSON

from app.db.base import Base


class DayOverride(Base):
    __tablename__ = "day_overrides"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)

    shift_type = Column(String(20), nullable=True)
    shift_start = Column(String(5), nullable=True)
    shift_end = Column(String(5), nullable=True)
    goal = Column(String(100), nullable=True)
    diet = Column(String(100), nullable=True)
    notes = Column(String(500), nullable=True)
    appointments = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
