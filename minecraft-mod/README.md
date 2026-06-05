# Minecraft Coach (Fabric 모드)

마인크래프트 인게임에서 백엔드 코칭 에이전트(FastAPI)를 호출하는 **클라이언트 모드**.
웹뷰(Streamlit)가 검증용이라면, 이 모드가 기획서가 말한 **실제 메인 클라이언트**다 — 둘 다 동일한 `POST /api/v1/chat/sync` API를 호출한다.

> 역할 #3 "마크 연결 세팅(플러그인화)"의 산출물. 인게임 ↔ 백엔드 **연결 기반**을 세팅하며, 그 위에 #4·#5(마크 기반 개발·고도화)가 기능을 쌓는다.

**스택**: Fabric · Minecraft 1.21.1 · Java 21 · Fabric API

---

## 사전 준비

- **JDK 21** (`java -version` → 21.x)
- 백엔드가 떠 있어야 함 — `project_code/`에서 `bash start.sh` → `http://localhost:8001`

## 빌드

```bash
cd minecraft-mod
./gradlew build          # 최초 1회는 마인크래프트/매핑 다운로드로 수 분 소요
# 산출물: build/libs/minecraft-coach-<버전>.jar
```

> Gradle은 동봉된 wrapper(`./gradlew`, 8.8)를 쓰므로 별도 설치가 필요 없다.

## 개발용 실행 (인게임 테스트)

```bash
./gradlew runClient      # 개발용 마인크래프트 클라이언트 실행
```

마인크래프트가 뜨면 → 싱글플레이 월드 입장 → 채팅에:

```
/coach 이제 뭐 해야 해?
/coach 철 곡괭이 만들고 싶은데 지금 돌 곡괭이밖에 없어
```

코치 응답이 채팅창에 출력된다. (`[코치] 물어보는 중…` → 답변)

## 정식 설치 (선택)

`build/libs/`의 jar를 Fabric Loader가 설치된 마인크래프트 `mods/` 폴더에 넣는다.
**Fabric API**도 함께 `mods/`에 있어야 한다.

---

## 백엔드 주소 설정

기본값은 `http://localhost:8001`. 다른 주소(배포 서버 등)로 바꾸려면 둘 중 하나:

```bash
# 1) JVM 시스템 프로퍼티
./gradlew runClient -Dcoach.backend.url=http://192.168.0.10:8001

# 2) 환경변수
COACH_BACKEND_URL=http://192.168.0.10:8001 ./gradlew runClient
```

대화 맥락용 `thread_id`는 게임 실행마다 자동 생성(`mc-<uuid>`)되어, 한 실행 동안 후속 질문이 이어진다.

---

## 구조

```
src/main/java/com/enderdragon/coach/
  CoachClientMod.java        클라이언트 진입점 (명령어 등록)
  CoachCommand.java          /coach <메시지> 명령어 → 호출 → 채팅 출력
  api/
    CoachApiClient.java      POST /api/v1/chat/sync 비동기 호출 (java.net.http)
    ChatRequest.java         요청 DTO (message, thread_id)
    ChatResponse.java        응답 DTO (answer, domain, sources, disclaimer)
    CoachApiException.java    호출 실패 → 사용자 친화 메시지
  config/
    CoachConfig.java         백엔드 주소 · 세션 thread_id
src/main/resources/
  fabric.mod.json            모드 메타데이터 (client 진입점)
```

### 백엔드 API 계약

| | |
| --- | --- |
| 엔드포인트 | `POST {backendUrl}/api/v1/chat/sync` |
| 요청 | `{ "message": "...", "thread_id": "mc-..." }` |
| 응답 | `{ "answer": "...", "domain": "", "sources": [], "disclaimer": "" }` |

---

## #4·#5를 위한 확장 포인트

- **이미지(스크린샷) 입력**: 백엔드 Vision 연동 시, 클라이언트 스크린샷을 멀티파트로 보내는 경로를 `CoachApiClient`에 추가.
- **스트리밍(SSE)**: 현재는 `/chat/sync`(단발). 토큰 스트리밍이 필요하면 백엔드 `POST /chat`(SSE)로 교체하고 채팅에 점진 출력.
- **전용 GUI**: 현재 1차 형태는 채팅 명령어. `Screen` 기반 코치 패널은 `CoachCommand`의 호출 로직을 재사용해 붙이면 된다.
- **인게임 상태 자동 수집**: 인벤토리·시간대 등을 모드에서 읽어 `message`에 함께 실어 보내면, 사용자가 일일이 입력할 필요가 줄어든다.
