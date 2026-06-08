"""세션 진척도 load/persist 노드 — 멀티턴 기억의 백본.

`load_state`는 그래프 시작에서 직전 진척도(목표·인벤토리)를 불러오고,
`persist_state`는 종료 전에 이번 턴 상태를 저장한다. 다음 턴이 직전 맥락을 이어받게 한다.
DB 장애는 best-effort로 무시한다(코칭은 계속 동작).
"""
import logging

from app.schemas import AgentState
from app.core.database import SessionLocal
from app import repositories

logger = logging.getLogger(__name__)


def load_state(state: AgentState) -> dict:
    """직전 턴의 진척도 스냅샷을 불러온다(목표·인벤토리)."""
    thread_id = state.get("thread_id")
    if not thread_id:
        return {}
    try:
        with SessionLocal() as db:
            snapshot = repositories.get_coaching_state(db, thread_id) or {}
    except Exception as e:
        logger.warning("load_state 실패(무시): %s", e)
        return {}
    return {
        "prior_goal_key": snapshot.get("goal_key", ""),
        "prior_last_inventory": snapshot.get("last_inventory", []),
    }


def reconcile(state: AgentState) -> dict:
    """직전 인벤토리와 비교해 새로 얻은 재료를 집어낸다(진행 상황 인식).

    첫 턴이거나 늘어난 재료가 없으면 빈 결과. responder가 이 노트로 진행을 격려한다.
    """
    prior = {i["item"]: i["count"] for i in state.get("prior_last_inventory", [])}
    if not prior:
        return {}
    current = {i["item"]: i["count"] for i in state.get("inventory", [])}
    gained = [
        {"item": item, "count": count - prior.get(item, 0)}
        for item, count in current.items()
        if count > prior.get(item, 0)
    ]
    return {"progress_note": gained} if gained else {}


def persist_state(state: AgentState) -> dict:
    """이번 턴의 목표·인벤토리를 저장한다(없으면 직전 값 유지)."""
    thread_id = state.get("thread_id")
    if not thread_id:
        return {}
    # 게임 모드면 현재 인벤토리를 저장, 웹이면 직전 값을 유지(웹은 인벤토리 없음).
    last_inventory = state["inventory"] if state.get("inventory_connected") else state.get("prior_last_inventory", [])
    snapshot = {
        "goal_key": state.get("goal_key") or state.get("prior_goal_key", ""),
        "last_inventory": last_inventory,
    }
    try:
        with SessionLocal() as db:
            repositories.upsert_coaching_state(db, thread_id, snapshot)
    except Exception as e:
        logger.warning("persist_state 실패(무시): %s", e)
    return {}
