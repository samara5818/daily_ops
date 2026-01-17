from datetime import datetime
from app.agents.planner_graph import run_planner

if __name__ == "__main__":
    user_id = "samara"
    now_iso = datetime.now().isoformat(timespec="seconds")

    result = run_planner(user_id=user_id, now_iso=now_iso)

    print("\n=== PROFILE ===")
    print(result["profile"])

    print("\n=== CONTEXT ===")
    print(result["context"])

    print("\n=== ACTIONS ===")
    for i, a in enumerate(result["actions"], 1):
        print(f"\nAction {i}:")
        print(a)

    print("\n=== WARNINGS ===")
    print(result["warnings"])
