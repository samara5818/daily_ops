import time
from datetime import datetime
from datetime import timedelta


from app.agents.planner_graph import run_planner
from app.services.schedule import normalize_actions_for_now
from app.services.scheduler import schedule_actions, list_jobs

if __name__ == "__main__":
    user_id = "samara"
    now = datetime.now()

    # 1) Create plan
    result = run_planner(user_id=user_id, now_iso=now.isoformat(timespec="seconds"))
    actions = result["actions"]

    # 2) Normalize schedule (push past times to next day)
    normalized = normalize_actions_for_now(actions, now)

    normalized[0]["run_at_iso"] = (now + timedelta(minutes=1)).replace(second=0, microsecond=0).isoformat(timespec="seconds")
    normalized[0]["title"] = "TEST: Daily Brief (1 min)"
    normalized[0]["message"] = "If you see this printed, APScheduler executor works."

    # 3) Schedule actions
    job_ids = schedule_actions(normalized)

    print("\n=== SCHEDULED JOBS ===")
    for j in list_jobs():
        print(j)

    print("\nScheduler is running... (Press CTRL+C to stop)")
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopped.")
