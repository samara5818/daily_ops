from datetime import datetime
from app.agents.planner_graph import run_planner
from app.services.schedule import normalize_actions_for_now

if __name__ == "__main__":
    user_id = "samara"
    now = datetime.now()

    result = run_planner(user_id=user_id, now_iso=now.isoformat(timespec="seconds"))
    actions = result["actions"]

    normalized = normalize_actions_for_now(actions, now)

    print("\n=== NOW ===")
    print(now.isoformat(timespec="seconds"))

    print("\n=== TODAY SETUP (NEXT RUN TIMES) ===")
    for i, a in enumerate(normalized, 1):
        print(f"\n{i}. {a['type']} | {a['category']} | {a['title']}")
        print(f"   run_at: {a['run_at_iso']} ({a['schedule'].get('timezone')})")
        print(f"   msg: {a['message']}")
