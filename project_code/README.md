# 마인크래프트 초보 가이드 챗봇 (Minecraft Guide Agent)

마인크래프트 초보자의 현재 상황(자원·진척도)을 파악해 목표까지의 **"다음 한 걸음"** 을 단계별로 안내하는 LLM 에이전트.

**스택**: FastAPI · LangGraph · MySQL · Qdrant · Upstage Solar · (검증용) Streamlit

> 이 디렉토리(`project_code/`)가 백엔드와 검증용 웹뷰의 루트입니다.
> 실제 메인 클라이언트는 후속 **Fabric 플러그인**이고, 웹뷰(Streamlit)는 챗봇 동작 검증용입니다. 둘 다 동일한 FastAPI API를 호출합니다.

---

## 빠른 시작 (팀원 온보딩)

사전 준비: [uv](https://docs.astral.sh/uv/) · Docker · `UPSTAGE_API_KEY` · (공유 벡터 사용 시) Qdrant Cloud `QDRANT_URL`/`QDRANT_API_KEY`

```bash
# 1) 환경변수
cp .env.example .env            # UPSTAGE_API_KEY 등 입력

# 2) 로컬 DB 기동 (MySQL + Qdrant)
docker compose up -d mysql qdrant

# 3) 의존성 설치 (Python 3.12 고정 — .python-version)
uv sync

# 4) DB 스키마 적용 (Alembic)
uv run alembic upgrade head

# 5) (데이터 수집자만) 위키 → Qdrant 적재
uv run python scripts/ingest_wiki.py --limit 50   # 시범(속도 보정)
uv run python scripts/ingest_wiki.py              # 전체 적재

# 6) 백엔드 + 웹뷰 실행
bash start.sh
#   Backend  → http://localhost:8001   (POST /api/v1/chat/sync)
#   Frontend → http://localhost:8002   (Streamlit)
```

---

## 협업 모델 (이 DB를 팀이 어떻게 쓰나)

- **MySQL**: 각자 로컬(docker-compose). 세션/메시지는 일회성 개발 데이터라 공유하지 않는다.
- **Qdrant 위키 벡터**: 공유 Qdrant Cloud에 **1회 적재** → 팀원은 `QDRANT_URL`/`QDRANT_API_KEY`로 연결만 (재임베딩 불필요).
- **스키마 변경**: `app/models.py` 수정 → `uv run alembic revision --autogenerate -m "변경 내용"` → 커밋. 팀원은 `uv run alembic upgrade head`로 동기화.
- **데이터 접근**: DB 내부를 몰라도 아래 함수만 호출하면 된다.
  - `app/repositories.py` — `get_or_create_session`, `append_message`, `get_recent_messages`
  - `app/vector_store.py` — `search_documents(query, n_results)`

---

## 구조

```
app/
  main.py            FastAPI 앱 (/health)
  api.py             /chat, /chat/sync (+ 세션·메시지 저장)
  graph.py           LangGraph: analyze → retrieve → respond (3노드)
  agents/            노드 구현 (query_analyzer / retrieval / responder)
  core/
    config.py        환경설정
    database.py      MySQL (SQLAlchemy engine/Session/Base)
    vector_db.py     Qdrant 클라이언트 (cloud/local)
    embedding.py     Upstage 임베딩 (동적 차원)
    llm.py           Upstage Solar
  models.py          User / ChatSession / Message
  repositories.py    DB 데이터 접근 계층 (팀 공용 인터페이스)
  vector_store.py    Qdrant 검색
alembic/             DB 마이그레이션
scripts/ingest_wiki.py   위키(Obsidian) → Qdrant 적재
frontend/ui.py       Streamlit 검증용 웹뷰
```

---

## 범위 (이슈 #5)

**포함**: DB 인프라(MySQL+Qdrant) · Alembic 스키마 · 위키 전체 적재 · 마인크래프트 리브랜딩 · 세션/메시지 저장 · 검증용 웹뷰 · 팀 온보딩

**후속 이슈**: 11노드 Agentic Workflow · Vision(스크린샷) · 세션 컨텍스트 메모리 · Fabric 플러그인 · 배포
