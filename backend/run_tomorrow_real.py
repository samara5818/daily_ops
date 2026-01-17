import time
from datetime import datetime, timedelta

from app.agents.planner_graph import run_planner
from app.services.schedule import normalize_actions_for_now
from app.services.scheduler import schedule_actions, list_jobs
from app.services.notify_email import send_email
from app.services.plan_email import build_plan_summary_email


if __name__ == "__main__":
    user_id = "samara"

    # Plan for tomorrow by "pretending now" is early tomorrow,
    # so tool_get_today_context() returns tomorrow's weekday/date.
    real_now = datetime.now()
    plan_now = (real_now + timedelta(days=1)).replace(hour=0, minute=5, second=0, microsecond=0)

    # 1) Generate plan (Planner Graph)
    result = run_planner(user_id=user_id, now_iso=plan_now.isoformat(timespec="seconds"))
    actions = result["actions"]

    # 2) Normalize schedule for tomorrow (relative to plan_now)
    normalized = normalize_actions_for_now(actions, plan_now)

    plan_date = plan_now.strftime("%Y-%m-%d")

    # 3) Send a complete plan email RIGHT NOW
    subject, body = build_plan_summary_email(
    user_id=user_id,
    plan_date=plan_date,
    actions=normalized,
    context=result.get("context", {})
    )
    send_email(subject, body)
    print(f"\n✅ Sent tomorrow plan email for {plan_date}")

    # 4) Schedule individual reminder emails for tomorrow
    job_ids = schedule_actions(normalized)

    print("\n=== SCHEDULED JOBS ===")
    for j in list_jobs():
        print(j)

    print("\nScheduler is running... keep this process alive to send reminders. (CTRL+C to stop)")
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopped.")
