from typing import Optional

from pydantic import BaseModel


class HealthProfileBase(BaseModel):
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None

    activity_level: Optional[str] = None
    workout_experience: Optional[str] = None

    dietary_goal: Optional[str] = None
    water_goal_ml: Optional[int] = None


class HealthProfileOut(HealthProfileBase):
    user_id: int

    class Config:
        from_attributes = True


class HealthProfileUpdate(HealthProfileBase):
    pass
