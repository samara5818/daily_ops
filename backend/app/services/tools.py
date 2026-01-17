from datetime import datetime
from typing import Dict, Any, List

from app.db.session import SessionLocal
from app.models.day_override import DayOverride
from app.models.user import User
from app.models.user_profile import UserProfile

TZ = "America/Los_Angeles"


def build_default_profile(user_id: str) -> Dict[str, Any]:
    return {
        "user_id": user_id,
        "name": None,
        "diet": "vegetarian",
        "goal": "gain_weight",
        "workout_time": "morning",
        "night_shifts": ["Monday", "Tuesday"],
        "job_search_daily_goal": 100,
        "quiet_hours": {"start": "23:00", "end": "07:00"},
        "timezone": TZ,
    }


def _get_user(db, user_id: str) -> User | None:
    if user_id.isdigit():
        return db.query(User).filter(User.id == int(user_id)).first()
    return db.query(User).filter(User.email == user_id).first()


def tool_get_user_profile(user_id: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        user = _get_user(db, user_id)
        if not user:
            return build_default_profile(user_id)

        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if not profile:
            return build_default_profile(str(user.id))

        return {
            "user_id": str(user.id),
            "name": profile.name or "",
            "diet": profile.diet or "",
            "goal": profile.goal or "",
            "workout_time": profile.workout_time or "",
            "night_shifts": profile.night_shifts or [],
            "job_search_daily_goal": profile.job_search_daily_goal or 0,
            "quiet_hours": {
                "start": profile.quiet_hours_start or "23:00",
                "end": profile.quiet_hours_end or "07:00",
            },
            "timezone": profile.timezone or TZ,
        }
    finally:
        db.close()

def tool_get_today_context(now_iso: str, user_id: str | None = None) -> Dict[str, Any]:
    # TODO: Replace with Calendar + time tracking + job tracker
    now = datetime.fromisoformat(now_iso)
    weekday = now.strftime("%A")
    context = {
        "date": now.strftime("%Y-%m-%d"),
        "weekday": weekday,
        "current_time": now.strftime("%H:%M"),
        "shift_type": "night" if weekday in ["Monday", "Tuesday"] else ("day" if weekday in ["Saturday", "Sunday"] else "off"),
        "work_shift": {
            "type": "night" if weekday in ["Monday", "Tuesday"] else ("day" if weekday in ["Saturday", "Sunday"] else "off"),
            "start": "22:00" if weekday in ["Monday", "Tuesday"] else ("09:00" if weekday in ["Saturday", "Sunday"] else None),
            "end": "07:30" if weekday in ["Monday", "Tuesday"] else ("21:00" if weekday in ["Saturday", "Sunday"] else None),
        },
        "signals": {
            "slept_hours_last_night": 6.5,
            "ate_breakfast": False,
            "job_apps_done_today": 0,
            "workout_done": False,
        },
    }

    if not user_id:
        return context

    db = SessionLocal()
    try:
        user = _get_user(db, user_id)
        if not user:
            return context
        override = (
            db.query(DayOverride)
            .filter(DayOverride.user_id == user.id, DayOverride.date == context["date"])
            .first()
        )
        if not override:
            return context

        override_data = {
            "shift_type": override.shift_type,
            "shift_start": override.shift_start,
            "shift_end": override.shift_end,
            "goal": override.goal,
            "diet": override.diet,
            "notes": override.notes,
            "appointments": override.appointments or [],
        }
        context["day_override"] = override_data

        if override.shift_type:
            context["shift_type"] = override.shift_type
            context["work_shift"]["type"] = override.shift_type
            context["work_shift"]["start"] = override.shift_start
            context["work_shift"]["end"] = override.shift_end

        return context
    finally:
        db.close()

def tool_sanity_validate_actions(actions: List[Dict[str, Any]]) -> List[str]:
    """Return list of warnings (empty if ok)."""
    warnings = []
    if not actions:
        warnings.append("No actions produced.")
        return warnings

    types = [a.get("type") for a in actions]
    if types.count("daily_brief") != 1:
        warnings.append("Must include exactly 1 daily_brief action.")

    if len(actions) > 6:
        warnings.append("Too many actions (>6).")

    for a in actions:
        if "schedule" not in a or "time" not in a["schedule"]:
            warnings.append(f"Missing schedule/time in action: {a.get('title','(no title)')}")
    return warnings
