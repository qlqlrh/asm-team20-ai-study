import operator
from uuid import uuid4
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    query: str
    history_text: str
    query_analysis: dict
    search_results: list[dict]
    structured_facts: list[str]
    final_answer: str
    domain: str
    iteration_count: int
    need_clarification: bool        # 추가 - kje
    clarification_question: str     # 추가 - kje
    prev_was_clarification: bool    # 직전 턴이 되묻기였는지(무한 되묻기 방지)
    inventory: list[dict]           # 마크 Mod에서 전달한 인벤토리 (웹은 항상 [])
    inventory_connected: bool       # 인벤토리 연동 클라이언트(게임 모드) 여부 (웹은 False)

class QueryAnalysis(BaseModel):
    keywords: list[str] = Field(description="keywords")
    domain: Literal["minecraft","general","out_of_scope"] = Field(description="domain")
    intent: str = Field(description="intent")
    status: Literal["success","insufficient"] = Field(description="status")

class ClarificationResult(BaseModel):
    need_clarification: bool = Field(description="추가 정보가 필요하면 true, 바로 답변 가능하면 false")
    question: str = Field(default="", description="need_clarification이 true일 때만 작성하는 한국어 되묻기 질문")

class InventoryItem(BaseModel):
    item: str
    count: int

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    thread_id: str = Field(default_factory=lambda: str(uuid4()))
    inventory: list[InventoryItem] = Field(default_factory=list)
    # 게임 모드(인벤토리 연동 클라이언트)는 True. 웹은 필드를 보내지 않아 기본 False.
    inventory_connected: bool = Field(default=False)

class ChatResponse(BaseModel):
    answer: str
    domain: str = ""
    sources: list[str] = Field(default_factory=list)
    disclaimer: str = ""

class StreamEvent(BaseModel):
    event: str = "message"
    node: str = ""
    data: str = ""
