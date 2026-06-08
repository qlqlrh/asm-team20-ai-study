"""web_search 노드 — RAG 커버리지가 부족할 때만 웹검색으로 근거를 보강한다.

retrieve 다음에 실행된다. 위키 검색 결과가 충분하거나(최고 유사도가 임계값 이상),
검색 API 키가 없으면 아무 일도 하지 않는다(best-effort). 부족하면 웹검색 결과를
기존 search_results 뒤에 병합해 코치가 더 풍부한 근거로 답하게 한다.
"""
import logging

from app.schemas import AgentState
from app.core.config import TAVILY_API_KEY, WEB_SEARCH_MIN_SCORE
from app.web_search import tavily_search

logger = logging.getLogger(__name__)


def _needs_web(results: list[dict], min_score: float) -> bool:
    """위키 검색이 빈약한지 판정한다(결과 없음 또는 최고 유사도가 임계값 미만)."""
    if not results:
        return True
    best = max((r.get("distance", 0.0) for r in results), default=0.0)
    return best < min_score


def search_web(state: AgentState) -> dict:
    """커버리지 부족 + 키 있을 때만 웹검색으로 보강한다. 그 외엔 빈 업데이트."""
    results = state.get("search_results", [])
    if not _needs_web(results, WEB_SEARCH_MIN_SCORE):
        return {}
    if not TAVILY_API_KEY:
        logger.info("WEB_SEARCH: 보강 필요하나 검색 API 키 없음 → 스킵")
        return {}

    keywords = state.get("query_analysis", {}).get("keywords", [])
    query = f"마인크래프트 {state.get('query', '')} {' '.join(keywords)}".strip()
    web = tavily_search(query, max_results=3)
    if not web:
        return {}
    logger.info("WEB_SEARCH: 위키 보강 — 웹 결과 %d건 병합", len(web))
    return {"search_results": results + web}
