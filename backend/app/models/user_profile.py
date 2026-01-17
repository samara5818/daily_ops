from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    diet = Column(String(100), nullable=True)
    goal = Column(String(100), nullable=True)
    workout_time = Column(String(50), nullable=True)
    night_shifts = Column(JSON, nullable=True)
    job_search_daily_goal = Column(Integer, nullable=True)
    quiet_hours_start = Column(String(5), nullable=True)
    quiet_hours_end = Column(String(5), nullable=True)
    timezone = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", backref="profile", lazy="joined")
