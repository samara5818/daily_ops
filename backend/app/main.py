from datetime import datetime
import os
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.agents.planner_graph import run_planner
from app.db.session import init_db, SessionLocal
from app.models.plan import Plan
from app.routers.auth import router as auth_router
from app.routers.day_override import router as day_override_router
from app.routers.profile import router as profile_router
from app.services.auth import get_current_user
from app.services.schedule import normalize_actions_for_now
from app.services.scheduler import get_scheduler, schedule_actions, list_jobs

app = FastAPI(title="Daily Ops Agent")
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(day_override_router)

allowed_origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:8001,http://127.0.0.1:8001").split(",")
PLAN_DAILY_LIMIT = int(os.getenv("PLAN_DAILY_LIMIT", "10"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    # Ensures scheduler starts when API starts
    get_scheduler()
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat(timespec="seconds")}


def _resolve_now(now_iso: Optional[str]) -> datetime:
    if not now_iso:
        return datetime.now()
    try:
        return datetime.fromisoformat(now_iso)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid now_iso. Use ISO format like 2026-01-17T09:00:00",
        ) from exc


def _enforce_plan_limit(user_id: str, plan_date: str) -> int:
    if not user_id.isdigit():
        return PLAN_DAILY_LIMIT
    db = SessionLocal()
    try:
        count = (
            db.query(Plan)
            .filter(Plan.user_id == int(user_id), Plan.date == plan_date)
            .count()
        )
    finally:
        db.close()
    remaining = max(0, PLAN_DAILY_LIMIT - count)
    if count >= PLAN_DAILY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Plan update limit reached for {plan_date}. Limit is {PLAN_DAILY_LIMIT} per day.",
        )
    return remaining


@app.get("/plan/{user_id}")
def plan(user_id: str, now_iso: Optional[str] = None, _current_user=Depends(get_current_user)):
    now = _resolve_now(now_iso)
    remaining = _enforce_plan_limit(user_id, now.strftime("%Y-%m-%d"))
    result = run_planner(user_id=user_id, now_iso=now.isoformat(timespec="seconds"))
    normalized = normalize_actions_for_now(result["actions"], now)
    return {
        "now": now.isoformat(timespec="seconds"),
        "profile": result.get("profile"),
        "context": result.get("context"),
        "actions": normalized,
        "warnings": result.get("warnings", []),
        "plan_remaining": remaining,
        "plan_limit": PLAN_DAILY_LIMIT,
    }


@app.get("/plan/me")
def plan_me(now_iso: Optional[str] = None, current_user=Depends(get_current_user)):
    now = _resolve_now(now_iso)
    remaining = _enforce_plan_limit(str(current_user.id), now.strftime("%Y-%m-%d"))
    result = run_planner(user_id=str(current_user.id), now_iso=now.isoformat(timespec="seconds"))
    normalized = normalize_actions_for_now(result["actions"], now)
    return {
        "now": now.isoformat(timespec="seconds"),
        "profile": result.get("profile"),
        "context": result.get("context"),
        "actions": normalized,
        "warnings": result.get("warnings", []),
        "plan_remaining": remaining,
        "plan_limit": PLAN_DAILY_LIMIT,
    }


@app.post("/plan-and-schedule/{user_id}")
def plan_and_schedule(user_id: str, now_iso: Optional[str] = None):
    now = _resolve_now(now_iso)
    remaining = _enforce_plan_limit(user_id, now.strftime("%Y-%m-%d"))
    result = run_planner(user_id=user_id, now_iso=now.isoformat(timespec="seconds"))
    normalized = normalize_actions_for_now(result["actions"], now)
    job_ids = schedule_actions(normalized)

    return {
        "now": now.isoformat(timespec="seconds"),
        "scheduled_count": len(job_ids),
        "job_ids": job_ids,
        "warnings": result.get("warnings", []),
        "next_jobs": list_jobs(),
        "plan_remaining": remaining,
        "plan_limit": PLAN_DAILY_LIMIT,
    }


@app.post("/plan-and-schedule/me")
def plan_and_schedule_me(now_iso: Optional[str] = None, current_user=Depends(get_current_user)):
    now = _resolve_now(now_iso)
    remaining = _enforce_plan_limit(str(current_user.id), now.strftime("%Y-%m-%d"))
    result = run_planner(user_id=str(current_user.id), now_iso=now.isoformat(timespec="seconds"))
    normalized = normalize_actions_for_now(result["actions"], now)
    job_ids = schedule_actions(normalized)

    return {
        "now": now.isoformat(timespec="seconds"),
        "scheduled_count": len(job_ids),
        "job_ids": job_ids,
        "warnings": result.get("warnings", []),
        "next_jobs": list_jobs(),
        "plan_remaining": remaining,
        "plan_limit": PLAN_DAILY_LIMIT,
    }


@app.get("/jobs")
def jobs():
    return {"jobs": list_jobs()}
