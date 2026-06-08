"""web_search 노드(폴백) 테스트.

네트워크/키 없이 결정론으로 검증한다: 커버리지 게이트, 키 없으면 스킵,
키 있을 때 웹 결과 병합. tavily_search는 가짜로 교체한다.
"""
from app.agents import web_searcher


def test_needs_web_빈결과나_낮은유사도면_True():
    assert web_searcher._needs_web([], 0.5) is True
    assert web_searcher._needs_web([{"distance": 0.2}], 0.5) is True


def test_needs_web_충분한_유사도면_False():
    assert web_searcher._needs_web([{"distance": 0.9}, {"distance": 0.3}], 0.5) is False


def test_커버리지_충분하면_웹검색_스킵(monkeypatch):
    called = {"n": 0}
    monkeypatch.setattr(web_searcher, "tavily_search", lambda *a, **k: called.__setitem__("n", called["n"] + 1) or [])
    out = web_searcher.search_web({"query": "철 곡괭이", "search_results": [{"distance": 0.9}]})
    assert out == {}
    assert called["n"] == 0  # 충분하므로 호출조차 안 함


def test_키_없으면_부족해도_스킵(monkeypatch):
    monkeypatch.setattr(web_searcher, "TAVILY_API_KEY", "")
    monkeypatch.setattr(web_searcher, "tavily_search", lambda *a, **k: [{"content": "x"}])
    out = web_searcher.search_web({"query": "철 곡괭이", "search_results": []})
    assert out == {}


def test_부족하고_키_있으면_웹결과를_병합(monkeypatch):
    monkeypatch.setattr(web_searcher, "TAVILY_API_KEY", "fake-key")
    web_doc = {"content": "웹 내용", "metadata": {"title": "위키 (웹)"}, "distance": 0.8, "source": "web"}
    monkeypatch.setattr(web_searcher, "tavily_search", lambda *a, **k: [web_doc])
    existing = [{"content": "약한 위키", "metadata": {"title": "위키"}, "distance": 0.1}]
    out = web_searcher.search_web({
        "query": "잘 안 나오는 질문",
        "query_analysis": {"keywords": ["철", "곡괭이"]},
        "search_results": existing,
    })
    assert out["search_results"] == existing + [web_doc]  # 기존 뒤에 병합


def test_웹검색_결과없으면_빈_업데이트(monkeypatch):
    monkeypatch.setattr(web_searcher, "TAVILY_API_KEY", "fake-key")
    monkeypatch.setattr(web_searcher, "tavily_search", lambda *a, **k: [])
    out = web_searcher.search_web({"query": "q", "search_results": []})
    assert out == {}
