import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from app.schemas import ChatRequest, ChatResponse, StreamEvent
from app.graph import create_graph
from app.core.database import SessionLocal
from app import repositories

router = APIRouter()
graph = create_graph()

HISTORY_TURNS = 6  # 직전 대화에서 불러올 메시지 수


def build_initial_state(message: str, history_text: str = "") -> dict:
    """사용자 메시지와 직전 대화 맥락으로 그래프 초기 상태를 생성한다."""
    return {
        "messages": [HumanMessage(content=message)],
        "query": message,
        "history_text": history_text,
        "query_analysis": {},
        "search_results": [],
        "final_answer": "",
        "domain": "",
        "iteration_count": 0,
    }


def _load_history_text(thread_id: str, limit: int = HISTORY_TURNS) -> str:
    """직전 대화 맥락을 텍스트로 불러온다. 실패해도 빈 문자열(응답을 막지 않음)."""
    try:
        db = SessionLocal()
        try:
            session = repositories.get_or_create_session(db, thread_id)
            msgs = repositories.get_recent_messages(db, session.id, limit=limit)
            return "\n".join(
                f"{'사용자' if m.role == 'user' else '가이드'}: {m.content}" for m in msgs
            )
        finally:
            db.close()
    except Exception:
        return ""


def _save_turn(thread_id: str, user_msg: str, assistant_msg: str) -> None:
    """세션을 보장하고 user/assistant 메시지를 저장한다 (best-effort)."""
    try:
        db = SessionLocal()
        try:
            session = repositories.get_or_create_session(db, thread_id)
            repositories.append_message(db, session.id, "user", user_msg)
            repositories.append_message(db, session.id, "assistant", assistant_msg)
        finally:
            db.close()
    except Exception:
        pass


@router.post("/chat/sync", response_model=ChatResponse)
async def chat_sync(request: ChatRequest):
    """동기 방식으로 전체 응답을 한 번에 반환한다."""
    history = _load_history_text(request.thread_id)
    result = await graph.ainvoke(build_initial_state(request.message, history))
    answer = result.get("final_answer", "")
    _save_turn(request.thread_id, request.message, answer)
    return ChatResponse(answer=answer, domain=result.get("domain", ""))


@router.post("/chat")
async def chat_stream(request: ChatRequest):
    """SSE 스트리밍으로 각 노드의 처리 과정을 실시간 전송한다."""
    history = _load_history_text(request.thread_id)

    async def gen():
        async for event in graph.astream_events(
            build_initial_state(request.message, history), version="v2"
        ):
            kind = event.get("event", "")
            if kind == "on_chain_end" and event.get("name") in ("analyze", "retrieve", "respond"):
                node_name = event["name"]
                node_output = event.get("data", {}).get("output", {})
                sse = StreamEvent(event="node", node=node_name, data=json.dumps(node_output, ensure_ascii=False, default=str))
                yield f"data: {sse.model_dump_json()}\n\n"

        # 최종 결과
        result = await graph.ainvoke(build_initial_state(request.message, history))
        answer = result.get("final_answer", "")
        _save_turn(request.thread_id, request.message, answer)
        done = StreamEvent(
            event="done",
            data=json.dumps({"answer": answer, "domain": result.get("domain", "")}, ensure_ascii=False),
        )
        yield f"data: {done.model_dump_json()}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
