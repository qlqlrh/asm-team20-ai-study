from app.schemas import AgentState
from app.vector_store import search_documents


def retrieve_context(state: AgentState) -> dict:
    """질문과 키워드를 결합하여 Qdrant에서 관련 문서를 검색한다."""
    query = state["query"]
    keywords = state.get("query_analysis", {}).get("keywords", [])
    # 키워드를 쿼리에 붙여서 검색 정확도를 높인다
    search_query = f"{query} {' '.join(keywords)}" if keywords else query
    # top-k를 넉넉히 가져와 레시피·수치 근거가 빠지지 않도록 한다
    return {"search_results": search_documents(query=search_query, n_results=5)}
