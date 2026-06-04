from app.schemas import AgentState
from app.vector_store import search_documents
from app.knowledge.facts import lookup_facts


def retrieve_context(state: AgentState) -> dict:
    """Qdrant 위키 검색 + 확정 사실(채굴 티어·레시피)을 함께 조회한다."""
    query = state["query"]
    keywords = state.get("query_analysis", {}).get("keywords", [])
    # 키워드를 쿼리에 붙여서 검색 정확도를 높인다
    search_query = f"{query} {' '.join(keywords)}" if keywords else query
    # top-k를 넉넉히 가져와 레시피·수치 근거가 빠지지 않도록 한다
    return {
        "search_results": search_documents(query=search_query, n_results=5),
        "structured_facts": lookup_facts(query, keywords),
    }
