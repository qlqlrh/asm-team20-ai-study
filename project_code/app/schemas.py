from uuid import uuid4
from typing import Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    query: str
    history_text: str
    query_analysis: dict
    search_results: list[dict]
    structured_facts: list[str]
    final_answer: str
    domain: str
    need_clarification: bool        # 추가 - kje
    clarification_question: str     # 추가 - kje
    prev_was_clarification: bool    # 직전 턴이 되묻기였는지(무한 되묻기 방지)
    inventory: list[dict]           # 마크 Mod에서 전달한 인벤토리 (웹은 항상 [])
    inventory_connected: bool       # 인벤토리 연동 클라이언트(게임 모드) 여부 (웹은 False)
    game_state: dict                # 인게임 상태(시간·체력·좌표 등). 모드만 전달, 없으면 {}
    goal_key: str                   # 해석된 제작 목표 item id (없으면 "")
    craft_gap: dict                 # compute_gap 결과(부족 자원·채굴 티어). 제작 목표 있을 때만
    todos: list[str]                # 게임 할 일 목록용 짧은 명령형 TODO (게임 모드에서만 생성)

class QueryAnalysis(BaseModel):
    keywords: list[str] = Field(description="keywords")
    domain: Literal["minecraft","general","out_of_scope"] = Field(description="domain")
    intent: str = Field(description="intent")
    status: Literal["success","insufficient"] = Field(description="status")

class ClarificationResult(BaseModel):
    need_clarification: bool = Field(description="추가 정보가 필요하면 true, 바로 답변 가능하면 false")
    question: str = Field(default="", description="need_clarification이 true일 때만 작성하는 한국어 되묻기 질문")

class TodoListResult(BaseModel):
    todos: list[str] = Field(
        default_factory=list,
        description="사용자가 수행할 행동만 담은 짧은 명령형 TODO 항목들 (예: '철 원석 3개 채굴', '화로 제작')",
    )

class InventoryItem(BaseModel):
    item: str
    count: int


class Position(BaseModel):
    x: int
    y: int
    z: int


class GameState(BaseModel):
    """인게임 상태 — 모드가 전송. 인벤토리만으로 모르는 생존/상황 파악에 쓴다."""
    time_of_day: str = ""           # "day" | "night"
    health: float = 0.0             # 0~20
    hunger: int = 0                 # 0~20
    dimension: str = ""             # "minecraft:overworld" 등
    position: Position | None = None


class SubgoalState(BaseModel):
    id: str
    title: str
    status: str = "pending"  # pending | active | done


class CoachingSnapshot(BaseModel):
    """세션별 코칭 진척도 스냅샷 (coaching_state.state에 JSON으로 저장).

    멀티턴에서 직전 계획 대비 진행을 비교(reconcile)하는 데 쓴다.
    """
    current_goal: str = ""
    goal_key: str = ""                                  # 정규화된 목표 키(예: minecraft:iron_pickaxe)
    plan: list[SubgoalState] = Field(default_factory=list)
    completed: list[str] = Field(default_factory=list)  # 완료한 subgoal id
    last_inventory: list[InventoryItem] = Field(default_factory=list)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    thread_id: str = Field(default_factory=lambda: str(uuid4()))
    inventory: list[InventoryItem] = Field(default_factory=list)
    # 게임 모드(인벤토리 연동 클라이언트)는 True. 웹은 필드를 보내지 않아 기본 False.
    inventory_connected: bool = Field(default=False)
    # 인게임 상태(시간·체력·좌표 등). 모드만 전송, 웹은 None.
    game_state: GameState | None = None

class ChatResponse(BaseModel):
    answer: str
    domain: str = ""
    sources: list[str] = Field(default_factory=list)
    disclaimer: str = ""
    todos: list[str] = Field(default_factory=list)  # 게임 할 일 목록용 짧은 TODO (웹은 빈 배열)

class StreamEvent(BaseModel):
    event: str = "message"
    node: str = ""
    data: str = ""
