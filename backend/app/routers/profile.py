from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.health_profile import HealthProfile
from app.models.user_profile import UserProfile
from app.schemas.profile import ProfileBundleOut, ProfileBundleUpdate, UserProfileOut, UserProfileUpdate
from app.services.auth import get_current_user
from app.services.tools import build_default_profile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=ProfileBundleOut)
def get_profile(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile:
        health = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
        return {"profile": profile, "health": health}

    defaults = build_default_profile(str(current_user.id))
    profile = UserProfile(
        user_id=current_user.id,
        name=defaults.get("name"),
        diet=defaults.get("diet"),
        goal=defaults.get("goal"),
        workout_time=defaults.get("workout_time"),
        night_shifts=defaults.get("night_shifts"),
        job_search_daily_goal=defaults.get("job_search_daily_goal"),
        quiet_hours_start=defaults.get("quiet_hours", {}).get("start"),
        quiet_hours_end=defaults.get("quiet_hours", {}).get("end"),
        timezone=defaults.get("timezone"),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    health = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    return {"profile": profile, "health": health}


@router.put("/me", response_model=ProfileBundleOut)
def update_profile(
    payload: ProfileBundleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    if payload.profile:
        for key, value in payload.profile.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)

    health = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if payload.health:
        if not health:
            health = HealthProfile(user_id=current_user.id)
            db.add(health)
        for key, value in payload.health.model_dump(exclude_unset=True).items():
            setattr(health, key, value)

    db.commit()
    db.refresh(profile)
    if health:
        db.refresh(health)
    return {"profile": profile, "health": health}
