# 마인크래프트 초보 가이드 챗봇 (엔더드래곤)

마인크래프트를 막 시작한 초보자의 상황(자원·진척도)을 파악해, 목표까지 가는 **"다음 한 걸음"**을 단계별로 안내하는 LLM 에이전트.

**스택**: FastAPI · LangGraph · MySQL · Qdrant(Cloud) · Upstage Solar · Fabric Mod(인게임 클라이언트) · (검증용) Streamlit

---

## 빠른 시작

```bash
git clone https://github.com/qlqlrh/asm-team20-ai-study.git
cd asm-team20-ai-study/project_code
cp .env.example .env          # UPSTAGE_API_KEY + 공유 QDRANT_URL/API_KEY 입력
docker compose up -d mysql    # 로컬 MySQL (Qdrant는 공유 클라우드)
uv sync
uv run alembic upgrade head
bash start.sh                 # Backend → :8001 · 웹뷰 → http://localhost:8002
```

👉 상세 절차·트러블슈팅: **[docs/백엔드_사용법.md](docs/백엔드_사용법.md)**

> 위키 벡터 5,923개는 **공유 Qdrant Cloud에 이미 적재**돼 있어 재적재가 필요 없다. 접속 정보만 받으면 바로 동작한다.

> **인게임으로 써보기**: Fabric 모드로 마인크래프트 안에서 코치를 직접 호출할 수 있다(웹뷰와 동일한 백엔드 API 사용) → **[minecraft-mod/README.md](minecraft-mod/README.md)**

---

## 문서

| 문서 | 내용 |
| --- | --- |
| [docs/백엔드_사용법.md](docs/백엔드_사용법.md) | 백엔드(FastAPI) 클론 → 로컬 실행 (팀원 온보딩) |
| [docs/기술_문서.md](docs/기술_문서.md) | 사용 기술·적용 방법 (아키텍처·워크플로우·RAG·DB·이슈 매핑) |
| [docs/인게임_사용법.md](docs/인게임_사용법.md) | Fabric 모드 인게임 사용법 |
| [docs/웹뷰_사용법.md](docs/웹뷰_사용법.md) | Streamlit 검증용 웹뷰 사용법 |
| [docs/스펙문서.md](docs/스펙문서.md) | 제품 설계·범위·협업 모델 |
| [docs/구현계획/](docs/구현계획/) | 이슈별 구현 절차·커밋 분해 (#5, #7) |
| [docs/알려진_이슈.md](docs/알려진_이슈.md) | 현재 알려진 품질 한계·해결 방향 |
| [project_code/README.md](project_code/README.md) | 백엔드·웹뷰 내부 구조·API 계약 |
| [minecraft-mod/README.md](minecraft-mod/README.md) | 인게임 Fabric 모드 — 빌드·사용법 |

## 구조

```
asm-team20-ai-study/
├── README.md          (이 파일 — 프로젝트 진입점)
├── docs/              설계·실행 문서 + 아키텍처 다이어그램
│   ├── 백엔드_사용법.md · 인게임_사용법.md · 웹뷰_사용법.md
│   ├── 기술_문서.md · 스펙문서.md · 알려진_이슈.md
│   └── 구현계획/       이슈별 구현 절차 (이슈-5, 이슈-7)
├── project_code/      백엔드(FastAPI·LangGraph) + 검증용 웹뷰(Streamlit)
└── minecraft-mod/     인게임 Fabric 모드 (실제 메인 클라이언트)
```

> 웹뷰와 Fabric 모드는 **동일한 FastAPI API**를 호출한다. 백엔드는 클라이언트에 종속되지 않는다.

## 진행 현황

**완료**: DB 인프라(MySQL + Qdrant Cloud) · Alembic 스키마 · 위키 전체 적재(RAG) · LangGraph 워크플로우(도메인 분류 · 되묻기 · 환각 방지) · 세션/메시지 저장 · 검증용 웹뷰 · **Fabric 인게임 모드**(코치 GUI · 인벤토리 인식 · 할 일 HUD)

**남은 작업**: 11노드 Agentic Workflow 확장 · Vision(스크린샷 분석) · 배포(EC2 · Qdrant Cloud)
