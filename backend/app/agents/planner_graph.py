import json
from typing import TypedDict, Dict, Any, List, Optional

from dotenv import load_dotenv
load_dotenv()


from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from app.agents.prompts import PLANNER_SYSTEM
from app.services.tools import (
    tool_get_user_profile,
    tool_get_today_context,
    tool_sanity_validate_actions,
)
from app.db.session import SessionLocal
from app.models.plan import Plan


def _fetch_previous_plan(user_id: str, plan_date: Optional[str]) -> Dict[str, Any]:
    if not plan_date:
        return {}
    db = SessionLocal()
    try:
        plan = (
            db.query(Plan)
            .filter(Plan.user_id == int(user_id) if user_id.isdigit() else Plan.user_id == -1)
            .filter(Plan.date == plan_date)
            .order_by(Plan.created_at.desc())
            .first()
        )
        if not plan:
            return {}
        return {
            "date": plan.date,
            "now_iso": plan.now_iso,
            "plan_json": plan.plan_json,
            "actions": plan.actions_json,
            "warnings": plan.warnings_json,
        }
    finally:
        db.close()


def _store_plan(user_id: str, now_iso: str, plan_json: Dict[str, Any], actions: List[Dict[str, Any]], warnings: List[str]) -> None:
    db = SessionLocal()
    try:
        plan_date = now_iso.split("T")[0]
        if not user_id.isdigit():
            return
        record = Plan(
            user_id=int(user_id),
            date=plan_date,
            now_iso=now_iso,
            plan_json=plan_json,
            actions_json=actions,
            warnings_json=warnings,
        )
        db.add(record)
        db.commit()
    finally:
        db.close()

class PlannerState(TypedDict, total=False):
    user_id: str
    now_iso: str
    profile: Dict[str, Any]
    context: Dict[str, Any]
    plan_json: Dict[str, Any]
    previous_plan: Dict[str, Any]
    actions: List[Dict[str, Any]]
    warnings: List[str]
    attempt: int
    error: Optional[str]

def load_context_node(state: PlannerState) -> PlannerState:
    user_id = state["user_id"]
    now_iso = state["now_iso"]
    profile = tool_get_user_profile(user_id)
    context = tool_get_today_context(now_iso, user_id=user_id)
    previous_plan = _fetch_previous_plan(user_id, context.get("date"))
    return {
        **state,
        "profile": profile,
        "context": context,
        "previous_plan": previous_plan,
        "attempt": state.get("attempt", 0),
    }

def llm_plan_node(state: PlannerState) -> PlannerState:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )

    payload = {
        "profile": state["profile"],
        "today": state["context"],
        "previous_plan": state.get("previous_plan"),
    }

    # The system prompt forces JSON output.
    msg = llm.invoke([
        {"role": "system", "content": PLANNER_SYSTEM},
        {"role": "user", "content": f"Create today's plan using this input:\n{json.dumps(payload, indent=2)}"},
    ])

    raw = msg.content.strip()
    try:
        plan = json.loads(raw)
        actions = plan.get("actions", [])
        return {**state, "plan_json": plan, "actions": actions, "error": None}
    except Exception as e:
        return {**state, "error": f"Invalid JSON from LLM: {e}", "plan_json": {}, "actions": []}

def validate_node(state: PlannerState) -> PlannerState:
    warnings = []
    if state.get("error"):
        warnings.append(state["error"])
    warnings.extend(tool_sanity_validate_actions(state.get("actions", [])))
    return {**state, "warnings": warnings}

def repair_node(state: PlannerState) -> PlannerState:
    """
    If validation fails, ask LLM to fix the JSON.
    We keep it simple: one repair attempt.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
    )

    attempt = state.get("attempt", 0) + 1
    if attempt > 1:
        # Give up after 1 repair attempt; return what we have.
        return {**state, "attempt": attempt}

    payload = {
        "profile": state.get("profile", {}),
        "today": state.get("context", {}),
        "current_plan": state.get("plan_json", {}),
        "warnings": state.get("warnings", []),
    }

    msg = llm.invoke([
        {"role": "system", "content": PLANNER_SYSTEM},
        {"role": "user", "content": "Fix the plan JSON to satisfy the schema and rules. Return JSON only.\n"
                                    + json.dumps(payload, indent=2)},
    ])

    raw = msg.content.strip()
    try:
        plan = json.loads(raw)
        actions = plan.get("actions", [])
        return {**state, "attempt": attempt, "plan_json": plan, "actions": actions, "error": None}
    except Exception as e:
        return {**state, "attempt": attempt, "error": f"Repair failed: {e}"}

def should_repair(state: PlannerState) -> str:
    if state.get("warnings"):
        # if there are warnings, try repair once
        if state.get("attempt", 0) < 1:
            return "repair"
    return "done"

def build_planner_graph():
    g = StateGraph(PlannerState)

    g.add_node("load_context", load_context_node)
    g.add_node("llm_plan", llm_plan_node)
    g.add_node("validate", validate_node)
    g.add_node("repair", repair_node)

    g.set_entry_point("load_context")
    g.add_edge("load_context", "llm_plan")
    g.add_edge("llm_plan", "validate")

    g.add_conditional_edges(
        "validate",
        should_repair,
        {
            "repair": "repair",
            "done": END
        }
    )
    g.add_edge("repair", "validate")

    return g.compile()

planner_graph = build_planner_graph()

def run_planner(user_id: str, now_iso: str) -> Dict[str, Any]:
    init: PlannerState = {"user_id": user_id, "now_iso": now_iso}
    out = planner_graph.invoke(init)
    result = {
        "profile": out.get("profile"),
        "context": out.get("context"),
        "actions": out.get("actions", []),
        "warnings": out.get("warnings", []),
    }
    _store_plan(
        user_id=user_id,
        now_iso=now_iso,
        plan_json=out.get("plan_json", {}),
        actions=result["actions"],
        warnings=result["warnings"],
    )
    return result
