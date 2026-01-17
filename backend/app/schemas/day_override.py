from typing import List, Optional

from pydantic import BaseModel


class Appointment(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    label: Optional[str] = None


class DayOverrideBase(BaseModel):
    shift_type: Optional[str] = None
    shift_start: Optional[str] = None
    shift_end: Optional[str] = None
    goal: Optional[str] = None
    diet: Optional[str] = None
    notes: Optional[str] = None
    appointments: Optional[List[Appointment]] = None


class DayOverrideOut(DayOverrideBase):
    id: int
    user_id: int
    date: str

    class Config:
        from_attributes = True


class DayOverrideUpdate(DayOverrideBase):
    pass
