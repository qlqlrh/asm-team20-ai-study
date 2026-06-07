"""세션 진척도 노드(load_state·reconcile·persist_state) 테스트.

load/persist는 SessionLocal을 SQLite 인메모리로 교체해 검증하고,
reconcile은 인벤토리 델타 계산이 결정론이라 그대로 검증한다.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
import app.models  # noqa: F401  Base.metadata에 테이블 등록
from app.agents import session_memory
from app.prompts.templates import format_progress_block


@pytest.fixture
def sqlite_db(monkeypatch):
    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    monkeypatch.setattr(session_memory, "SessionLocal", sessionmaker(bind=engine, future=True))


def test_저장한_진척도를_다음_턴에_로드한다(sqlite_db):
    session_memory.persist_state({
        "thread_id": "t1",
        "goal_key": "minecraft:iron_pickaxe",
        "inventory": [{"item": "minecraft:oak_log", "count": 5}],
        "inventory_connected": True,
    })
    loaded = session_memory.load_state({"thread_id": "t1"})
    assert loaded["prior_goal_key"] == "minecraft:iron_pickaxe"
    assert loaded["prior_last_inventory"] == [{"item": "minecraft:oak_log", "count": 5}]


def test_목표없는_턴은_직전_목표를_유지한다(sqlite_db):
    session_memory.persist_state({"thread_id": "t1", "goal_key": "minecraft:furnace",
                                  "inventory": [], "inventory_connected": True})
    # 다음 턴: 목표 미해석(goal_key 없음) + 직전 목표 로드 상태로 저장
    session_memory.persist_state({"thread_id": "t1", "goal_key": "",
                                  "prior_goal_key": "minecraft:furnace",
                                  "inventory": [], "inventory_connected": True})
    assert session_memory.load_state({"thread_id": "t1"})["prior_goal_key"] == "minecraft:furnace"


def test_없는_세션은_빈_진척도를_반환한다(sqlite_db):
    # 유효 thread_id지만 저장된 게 없으면 빈 prior로 채워 반환한다.
    assert session_memory.load_state({"thread_id": "nope"}) == {"prior_goal_key": "", "prior_last_inventory": []}


def test_thread_id_없으면_skip():
    assert session_memory.load_state({}) == {}
    assert session_memory.persist_state({}) == {}


def test_reconcile_새로_얻은_재료를_집어낸다():
    out = session_memory.reconcile({
        "prior_last_inventory": [{"item": "minecraft:cobblestone", "count": 1}],
        "inventory": [{"item": "minecraft:cobblestone", "count": 4}, {"item": "minecraft:raw_iron", "count": 2}],
    })
    note = {p["item"]: p["count"] for p in out["progress_note"]}
    assert note["minecraft:cobblestone"] == 3
    assert note["minecraft:raw_iron"] == 2


def test_reconcile_첫_턴이나_변화없으면_빈값():
    assert session_memory.reconcile({"prior_last_inventory": [], "inventory": [{"item": "x", "count": 1}]}) == {}
    same = [{"item": "minecraft:dirt", "count": 3}]
    assert session_memory.reconcile({"prior_last_inventory": same, "inventory": same}) == {}


def test_진행_블록_포맷():
    block = format_progress_block([{"item": "minecraft:cobblestone", "count": 3}])
    assert "조약돌 3개" in block
    assert format_progress_block([]) == ""
