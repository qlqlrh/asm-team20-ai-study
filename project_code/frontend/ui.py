import os
from uuid import uuid4

import httpx
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
SYNC_ENDPOINT = f"{BACKEND_URL}/api/v1/chat/sync"

st.set_page_config(page_title="마인크래프트 초보 가이드", page_icon="🧱", layout="wide")
st.title("🧱 마인크래프트 초보 가이드")
st.caption("막막할 때, 지금 내 상황에서 '다음 한 걸음'을 물어보세요. (예: \"방금 시작했는데 뭐부터 해야 해?\")")

# 같은 thread_id로 보내면 대화 맥락이 같은 세션으로 DB에 이어서 저장된다
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("마인크래프트에 대해 물어보세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("길을 찾는 중..."):
            try:
                resp = httpx.post(
                    SYNC_ENDPOINT,
                    json={"message": prompt, "thread_id": st.session_state.thread_id},
                    timeout=60.0,
                )
                resp.raise_for_status()
                answer = resp.json().get("answer", "")
            except Exception as e:
                # 검증용 UI라 에러를 그대로 노출한다
                answer = f"오류: {e}"
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

with st.sidebar:
    st.caption(f"세션 ID: `{st.session_state.thread_id[:8]}…`")
    if st.button("새 대화 시작"):
        st.session_state.thread_id = str(uuid4())
        st.session_state.messages = []
        st.rerun()
