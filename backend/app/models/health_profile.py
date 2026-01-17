from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func

from app.db.base import Base


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)

    height_cm = Column(Numeric(5, 2), nullable=True)
    weight_kg = Column(Numeric(5, 2), nullable=True)
    target_weight_kg = Column(Numeric(5, 2), nullable=True)

    activity_level = Column(String(32), nullable=True)
    workout_experience = Column(String(32), nullable=True)

    dietary_goal = Column(String(32), nullable=True)
    water_goal_ml = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
