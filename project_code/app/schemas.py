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

class QueryAnalysis(BaseModel):
    keywords: list[str] = Field(description="keywords")
    domain: Literal["minecraft","general","out_of_scope"] = Field(description="domain")
    intent: str = Field(description="intent")
    status: Literal["success","insufficient"] = Field(description="status")

class ClarificationResult(BaseModel):
    need_clarification: bool = Field(description="추가 정보가 필요하면 true, 바로 답변 가능하면 false")
    question: str = Field(default="", description="need_clarification이 true일 때만 작성하는 한국어 되묻기 질문")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    thread_id: str = Field(default_factory=lambda: str(uuid4()))

class ChatResponse(BaseModel):
    answer: str
    domain: str = ""
    sources: list[str] = Field(default_factory=list)
    disclaimer: str = ""

class StreamEvent(BaseModel):
    event: str = "message"
    node: str = ""
    data: str = ""
