from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv
load_dotenv()

from app.services.notify_email import send_email

from app.services.notify_telegram import send_telegram_message

def format_email(action: Dict[str, Any]) -> tuple[str, str]:
    category = action.get("category", "reminder").upper()
    title = action.get("title", "Reminder")
    msg = action.get("message", "")
    run_at = action.get("run_at_iso", "")

    subject = f"[DailyOps] {category}: {title}"
    body = (
        f"{title}\n"
        f"{'-' * len(title)}\n"
        f"{msg}\n\n"
        f"Scheduled: {run_at}\n"
        f"Type: {action.get('type')}\n"
        f"Priority: {action.get('priority')}\n"
    )
    return subject, body


def format_action_message(action: Dict[str, Any]) -> str:
    emoji = {
        "health": "🥗",
        "workout": "🏋️",
        "job_search": "🧑‍💻",
        "review": "📝",
    }.get(action.get("category"), "🔔")

    title = action.get("title", "Reminder")
    msg = action.get("message", "")
    run_at = action.get("run_at_iso", "")

    return f"{emoji} {title}\n{msg}\n\n⏰ {run_at}"


def execute_action(action: Dict[str, Any]) -> None:
    now = datetime.now().isoformat(timespec="seconds")

    print("\n" + "=" * 60)
    print(f"[EXECUTE] {now}")
    print(f"title: {action.get('title')}")
    print(f"message: {action.get('message')}")
    print("=" * 60)

    subject, body = format_email(action)
    send_email(subject, body)
