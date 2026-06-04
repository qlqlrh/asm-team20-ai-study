import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.schemas import AgentState, ClarificationResult
from app.core.llm import get_llm

logger = logging.getLogger(__name__)

CLARIFIER_SYSTEM = """당신은 마인크래프트 초보자 가이드 챗봇입니다.
사용자 질문을 보고, 유용한 답변을 하기 위해 추가 정보가 필요한지 판단합니다.

추가 정보가 필요한 경우 (need_clarification: true):
- "뭐 해야 해?", "어떻게 해?" 처럼 현재 자원·보유 아이템·진척도를 모르면 구체적 안내가 불가능한 질문
- 목표나 상황이 너무 막연해서 단계별 경로를 알려주기 어려운 질문

바로 답변하는 경우 (need_clarification: false):
- "철 곡괭이 만드는 법", "크리퍼가 뭐야?" 처럼 목표/사실이 명확한 질문
- 이전 대화에서 이미 사용자 상황(보유 아이템·진척도)을 파악한 경우
- 사용자가 이미 이전 질문에 답하며 현재 상황을 설명한 경우"""


def _already_answered_clarification(history_text: str) -> bool:
    """직전 가이드 발화가 질문(?)으로 끝나면, 사용자가 이미 답변한 것으로 간주해 재질문을 막는다."""
    if not history_text:
        return False
    guide_lines = [
        l.strip() for l in history_text.strip().split("\n")
        if l.strip().startswith("가이드:")
    ]
    return bool(guide_lines) and guide_lines[-1].rstrip().endswith("?")


def check_and_clarify(state: AgentState) -> dict:
    history = state.get("history_text", "")

    # 직전 턴에서 이미 되묻기를 했으면 스킵 → 루프 방지
    if _already_answered_clarification(history):
        logger.warning("CLARIFIER: 직전 턴 되묻기 감지 → 스킵")
        return {"need_clarification": False, "clarification_question": ""}

    llm = get_llm(temperature=0.0)
    query = state["query"]
    user_content = query if not history else f"[이전 대화]\n{history}\n\n[현재 질문] {query}"

    try:
        structured_llm = llm.with_structured_output(ClarificationResult)
        result = structured_llm.invoke([
            SystemMessage(content=CLARIFIER_SYSTEM),
            HumanMessage(content=user_content),
        ])
        logger.warning("CLARIFIER: need=%s question=%s", result.need_clarification, result.question)
        return {
            "need_clarification": result.need_clarification,
            "clarification_question": result.question,
        }
    except Exception as e:
        logger.warning("Clarifier failed: %s", e)
        return {"need_clarification": False, "clarification_question": ""}
