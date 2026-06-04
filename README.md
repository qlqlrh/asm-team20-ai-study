# 마인크래프트 초보 가이드 챗봇 (엔더드래곤)

마인크래프트를 막 시작한 초보자의 상황(자원·진척도)을 파악해, 목표까지 가는 **"다음 한 걸음"**을 단계별로 안내하는 LLM 에이전트.

**스택**: FastAPI · LangGraph · MySQL · Qdrant(Cloud) · Upstage Solar · (검증용) Streamlit

---

## 빠른 시작

```bash
git clone https://github.com/qlqlrh/asm-team20-ai-study.git
cd asm-team20-ai-study/project_code
cp .env.example .env          # UPSTAGE_API_KEY + 공유 QDRANT_URL/API_KEY 입력
docker compose up -d mysql    # 로컬 MySQL (Qdrant는 공유 클라우드)
uv sync
uv run alembic upgrade head
bash start.sh                 # → http://localhost:8002
```

👉 상세 절차·트러블슈팅: **[docs/실행_가이드.md](docs/실행_가이드.md)**

> 위키 벡터 5,923개는 **공유 Qdrant Cloud에 이미 적재**돼 있어 재적재가 필요 없다. 접속 정보만 받으면 바로 동작한다.

---

## 문서

| 문서 | 내용 |
| --- | --- |
| [docs/실행_가이드.md](docs/실행_가이드.md) | 클론 → 로컬 실행 (팀원 온보딩) |
| [docs/스펙문서.md](docs/스펙문서.md) | 제품 설계·범위·협업 모델 |
| [docs/구현계획.md](docs/구현계획.md) | 이슈 #5 구현 절차·커밋 분해 |
| [docs/알려진_이슈.md](docs/알려진_이슈.md) | 현재 알려진 품질 한계·해결 방향 |
| [project_code/README.md](project_code/README.md) | 앱 내부 구조·API 계약 |

## 구조

```
asm-team20-ai-study/
├── README.md          (이 파일 — 프로젝트 진입점)
├── docs/              설계·실행 문서
│   ├── 실행_가이드.md
│   ├── 스펙문서.md
│   ├── 구현계획.md
│   └── 알려진_이슈.md
└── project_code/      백엔드 + 검증용 웹뷰 (앱 루트)
```

## 범위 (이슈 #5)

**포함**: DB 인프라(MySQL + Qdrant Cloud) · Alembic 스키마 · 위키 전체 적재 · 마인크래프트 리브랜딩 · 세션/메시지 저장 · 검증용 웹뷰 · 팀 온보딩 문서

**후속 이슈**: 11노드 Agentic Workflow · Vision(스크린샷) · Fabric 플러그인 클라이언트 · 배포
