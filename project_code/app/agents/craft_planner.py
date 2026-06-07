"""craft_plan 노드 — 제작 목표를 해석해 결정론적 부족 자원을 계산한다.

질문에서 제작 목표 아이템을 찾으면 compute_gap으로 부족 재료·채굴 티어 차단을
계산해 상태에 싣는다. responder가 이 결과를 프롬프트에 주입해 검증된 수치로 안내한다.
제작 목표가 없으면(생존·탐험·막연형 등) 아무것도 하지 않고 기존 흐름을 유지한다.
"""
import logging

from app.schemas import AgentState
from app.knowledge import planner
from app.knowledge.goal_resolver import resolve_craft_target

logger = logging.getLogger(__name__)


def plan_craft(state: AgentState) -> dict:
    target = resolve_craft_target(state.get("query", ""))
    if not target:
        return {}
    gap = planner.compute_gap(target, state.get("inventory", []))
    logger.info("CRAFT_PLAN: target=%s ready=%s gather=%d", target, gap["ready"], len(gap["gather"]))
    return {"goal_key": target, "craft_gap": gap}
