from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.day_override import DayOverride
from app.schemas.day_override import DayOverrideOut, DayOverrideUpdate
from app.services.auth import get_current_user

router = APIRouter(prefix="/day-overrides", tags=["day_overrides"])


def _normalize_date(date: str) -> str:
    if len(date) != 10:
        raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD")
    return date


@router.get("/{date}", response_model=DayOverrideOut)
def get_day_override(date: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    date = _normalize_date(date)
    override = (
        db.query(DayOverride)
        .filter(DayOverride.user_id == current_user.id, DayOverride.date == date)
        .first()
    )
    if not override:
        raise HTTPException(status_code=404, detail="No override for date")
    return override


@router.put("/{date}", response_model=DayOverrideOut)
def upsert_day_override(
    date: str,
    payload: DayOverrideUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    date = _normalize_date(date)
    override = (
        db.query(DayOverride)
        .filter(DayOverride.user_id == current_user.id, DayOverride.date == date)
        .first()
    )
    if not override:
        override = DayOverride(user_id=current_user.id, date=date)
        db.add(override)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(override, key, value)

    db.commit()
    db.refresh(override)
    return override
