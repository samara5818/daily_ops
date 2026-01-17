from typing import List, Optional

from pydantic import BaseModel

from app.schemas.health import HealthProfileOut, HealthProfileUpdate


class UserProfileBase(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    diet: Optional[str] = None
    goal: Optional[str] = None
    workout_time: Optional[str] = None
    night_shifts: Optional[List[str]] = None
    job_search_daily_goal: Optional[int] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None


class UserProfileOut(UserProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class UserProfileUpdate(UserProfileBase):
    pass


class ProfileBundleOut(BaseModel):
    profile: UserProfileOut
    health: Optional[HealthProfileOut] = None


class ProfileBundleUpdate(BaseModel):
    profile: Optional[UserProfileUpdate] = None
    health: Optional[HealthProfileUpdate] = None
