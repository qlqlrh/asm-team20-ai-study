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


def check_and_clarify(state: AgentState) -> dict:
    history = state.get("history_text", "")

    # 직전 턴이 실제 '되묻기'였으면 스킵 → 무한 되묻기 방지.
    # (되묻기 문구가 '?'로 끝나지 않는 경우가 많아, 텍스트가 아니라 상태로 판정한다.)
    if state.get("prev_was_clarification"):
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
