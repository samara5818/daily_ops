from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.auth import Token, UserCreate, UserOut
from app.services.auth import create_access_token, get_current_user, get_password_hash, verify_password
from app.services.tools import build_default_profile

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if len(payload.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password must be at most 72 bytes")

    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        is_active=True,
        email_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    defaults = build_default_profile(str(user.id))
    profile = UserProfile(
        user_id=user.id,
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
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if len(form_data.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at most 72 bytes")
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.email)
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
