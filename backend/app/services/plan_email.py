from typing import Dict, Any, List


def build_plan_summary_email(user_id: str, plan_date: str, actions: List[Dict[str, Any]], context: Dict[str, Any]) -> tuple[str, str]:
    subject = f"[DailyOps] Tomorrow Plan ({plan_date}) - {user_id}"

    shift = context.get("work_shift", {})
    shift_line = "OFF"
    if shift.get("type") in ("day", "night"):
        shift_line = f"{shift.get('type').upper()} SHIFT {shift.get('start')}–{shift.get('end')}"

    lines = []
    lines.append(f"Tomorrow Plan ({plan_date})")
    lines.append("=" * 32)
    lines.append(f"Shift: {shift_line}")
    lines.append("")

    # Pull daily brief to show at top
    brief = next((a for a in actions if a.get("type") == "daily_brief"), None)
    if brief:
        lines.append("Daily Brief")
        lines.append("-" * 10)
        lines.append(brief.get("message", ""))
        lines.append("")

    lines.append("Schedule")
    lines.append("-" * 8)

    actions_sorted = sorted(actions, key=lambda a: a.get("run_at_iso") or "9999")
    for i, a in enumerate(actions_sorted, 1):
        run_at = a.get("run_at_iso", "")
        title = a.get("title", "")
        category = a.get("category", "")
        msg = a.get("message", "")
        lines.append(f"{i}. {run_at} | {category} | {title}")
        lines.append(f"   {msg}")
        lines.append("")

    body = "\n".join(lines)
    return subject, body
