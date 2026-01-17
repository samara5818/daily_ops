from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, List

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

from app.services.executor import execute_action

_scheduler: BackgroundScheduler | None = None

def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        _scheduler.start()
    return _scheduler

def schedule_actions(actions: List[Dict[str, Any]]) -> List[str]:
    """
    Schedule all actions using their run_at_iso.
    Returns a list of scheduled job IDs.
    """
    sched = get_scheduler()
    job_ids: List[str] = []

    for idx, action in enumerate(actions, 1):
        run_at_iso = action.get("run_at_iso")
        if not run_at_iso:
            # skip invalid actions
            continue

        run_at = datetime.fromisoformat(run_at_iso)
        job_id = f"{action.get('type','action')}-{idx}-{run_at.strftime('%Y%m%d%H%M%S')}"

        trigger = DateTrigger(run_date=run_at)
        sched.add_job(
            execute_action,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            kwargs={"action": action},
            misfire_grace_time=60 * 10,  # 10 minutes grace
            coalesce=True,
            max_instances=1,
        )
        job_ids.append(job_id)

    return job_ids

def list_jobs() -> List[Dict[str, Any]]:
    sched = get_scheduler()
    jobs = []
    for j in sched.get_jobs():
        jobs.append({
            "id": j.id,
            "next_run_time": j.next_run_time.isoformat() if j.next_run_time else None,
        })
    return jobs
