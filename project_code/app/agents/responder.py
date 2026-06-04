from langchain_core.messages import SystemMessage, HumanMessage
from app.schemas import AgentState
from app.core.llm import get_llm
from app.prompts.templates import (
    RESPONDER_SYSTEM, RESPONDER_FORMAT_GUIDE,
    GENERAL_RESPONSE_SYSTEM, OUT_OF_SCOPE_RESPONSE,
)


def generate_answer(state: AgentState) -> dict:
    """도메인에 따라 적절한 답변을 생성한다.

    - out_of_scope: 고정 안내 응답
    - general: temperature 0.5로 가벼운 답변
    - minecraft: temperature 0.3으로 위키 검색 결과 기반 코칭 응답
    """
    domain = state.get("domain", "minecraft")
    query = state["query"]
    iteration = state.get("iteration_count", 0) + 1

    # 범위 밖 질문 — 고정 안내
    if domain == "out_of_scope":
        return {"final_answer": OUT_OF_SCOPE_RESPONSE, "iteration_count": iteration}

    # 일반 질문 — 가벼운 답변
    if domain == "general":
        llm = get_llm(temperature=0.5)
        r = llm.invoke([
            SystemMessage(content=GENERAL_RESPONSE_SYSTEM),
            HumanMessage(content=query),
        ])
        return {"final_answer": r.content, "iteration_count": iteration}

    # 마인크래프트 질문 — 위키 검색 결과 기반 코칭
    llm = get_llm(temperature=0.3)
    results = state.get("search_results", [])
    parts = [
        f"[{i+1}] ({doc.get('metadata', {}).get('title', '')})\n{doc.get('content', '')}"
        for i, doc in enumerate(results)
    ]
    ctx = "\n\n".join(parts) if parts else "(검색 결과 없음)"

    r = llm.invoke([
        SystemMessage(content=f"{RESPONDER_SYSTEM}\n{RESPONDER_FORMAT_GUIDE}"),
        HumanMessage(content=f"질문: {query}\n\n참고 위키:\n{ctx}"),
    ])
    return {"final_answer": r.content, "iteration_count": iteration}
