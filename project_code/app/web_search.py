"""웹검색 클라이언트(Tavily) — RAG 커버리지 부족 시 근거를 보강한다.

검색 결과를 Qdrant 검색(search_documents)과 동일한 형태로 변환해, 코치 응답이
위키 문서와 똑같이 다룰 수 있게 한다. API 키가 없거나 호출이 실패하면 빈 목록을
반환해(best-effort) 기존 흐름을 깨지 않는다.
"""
import logging

import httpx

from app.core.config import TAVILY_API_KEY

logger = logging.getLogger(__name__)

_TAVILY_URL = "https://api.tavily.com/search"


def tavily_search(query: str, max_results: int = 3) -> list[dict]:
    """Tavily 웹검색 결과를 search_results 형식으로 반환한다(키 없거나 실패면 []).

    반환: [{"content", "metadata": {"title", "url"}, "distance", "source": "web"}, ...]
    distance에는 Tavily 관련도 점수를 담아 위키 결과와 동일하게 다룬다.
    """
    if not TAVILY_API_KEY:
        return []
    try:
        resp = httpx.post(
            _TAVILY_URL,
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning("Tavily 검색 실패(무시): %s", e)
        return []

    results = []
    for r in data.get("results", []):
        title = (r.get("title") or "").strip()
        results.append({
            "content": r.get("content", ""),
            "metadata": {"title": f"{title} (웹)" if title else "웹 검색", "url": r.get("url", "")},
            "distance": r.get("score", 0.0),
            "source": "web",
        })
    return results
