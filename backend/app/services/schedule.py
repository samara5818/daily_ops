from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, Any, List

def _parse_hhmm(hhmm: str) -> tuple[int, int]:
    h, m = hhmm.split(":")
    return int(h), int(m)

def normalize_actions_for_now(actions: List[Dict[str, Any]], now: datetime) -> List[Dict[str, Any]]:
    """
    If an action is scheduled earlier than 'now', push it to the next day at the same HH:MM.
    Adds computed fields:
      - run_at_iso: ISO timestamp (local naive) for execution
      - run_date: YYYY-MM-DD
    """
    normalized = []

    for a in actions:
        sched = a.get("schedule", {})
        time_str = sched.get("time", "09:00")  # fallback
        hour, minute = _parse_hhmm(time_str)

        run_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # If already passed, move to next day
        if run_at <= now:
            run_at = run_at + timedelta(days=1)

        a2 = dict(a)
        a2["run_at_iso"] = run_at.isoformat(timespec="seconds")
        a2["run_date"] = run_at.strftime("%Y-%m-%d")
        normalized.append(a2)

    # Sort by execution time
    normalized.sort(key=lambda x: x["run_at_iso"])
    return normalized
