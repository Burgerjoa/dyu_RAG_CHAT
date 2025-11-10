"""
동양대학교 RAG 챗봇 Streamlit UI

이 모듈은 RAG 시스템을 위한 웹 인터페이스를 제공합니다.
"""

import streamlit as st
import requests
from typing import Dict, List, Any
import time
import os

# 페이지 설정
st.set_page_config(
    page_title="동양대학교 AI 도우미",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# API 엔드포인트 (환경변수에서 읽기, 기본값은 localhost)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_URL = f"{API_BASE_URL}/chat"
HEALTH_URL = f"{API_BASE_URL}/health"


def check_api_health() -> bool:
    """
    API 서버 상태 확인

    Returns:
        서버가 정상 작동하면 True, 아니면 False
    """
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        return response.status_code == 200
    except:
        return False


def get_answer(question: str) -> Dict[str, Any]:
    """
    API를 통해 답변 받기

    Args:
        question: 사용자 질문

    Returns:
        답변과 출처를 포함한 딕셔너리

    Raises:
        Exception: API 호출 실패 시
    """
    try:
        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise Exception("API 서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인해주세요.")
    except requests.exceptions.Timeout:
        raise Exception("요청 시간이 초과되었습니다. 다시 시도해주세요.")
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get("detail", str(e))
        raise Exception(f"API 오류: {error_detail}")
    except Exception as e:
        raise Exception(f"알 수 없는 오류: {str(e)}")


def initialize_session_state():
    """세션 상태 초기화"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_available" not in st.session_state:
        st.session_state.api_available = check_api_health()


def main():
    """메인 애플리케이션"""

    # 세션 상태 초기화
    initialize_session_state()

    # 타이틀
    st.title("🎓 동양대학교 AI 도우미")
    st.markdown("학사 관련 질문에 답변해드립니다!")

    # 사이드바
    with st.sidebar:
        st.header("ℹ️ 정보")
        st.markdown("""
        **동양대학교 AI 도우미**는 RAG 기술을 활용하여
        학사 관련 질문에 정확하게 답변합니다.

        ### 질문 예시
        - 장학금 받으려면?
        - 졸업 학점은?
        - 도서관 운영시간은?
        - 기숙사 신청 방법은?

        ### 기술 스택
        - LangChain
        - OpenAI GPT-3.5
        - ChromaDB
        - FastAPI
        - Streamlit
        """)

        # API 상태 표시
        st.divider()
        st.subheader("🔌 서버 상태")
        if st.session_state.api_available:
            st.success("✅ API 서버 연결됨")
        else:
            st.error("❌ API 서버 연결 안 됨")
            st.warning("FastAPI 서버를 먼저 실행해주세요:\n```\npython backend/main.py\n```")

        # 대화 초기화 버튼
        st.divider()
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # 대화 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # 출처 표시 (봇 메시지인 경우)
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 참고 문서"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**{i}. {source['title']}**")
                        st.markdown(f"🔗 [{source['source']}]({source['source']})")
                        st.caption(source['content'])
                        if i < len(message["sources"]):
                            st.divider()

    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요..."):

        # API 서버 상태 재확인
        if not check_api_health():
            st.error("❌ API 서버에 연결할 수 없습니다. FastAPI 서버를 먼저 실행해주세요.")
            return

        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(prompt)

        # 사용자 메시지 저장
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # 봇 응답 생성
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 답변을 생성하는 중...")

            try:
                # API 호출
                with st.spinner("처리 중..."):
                    result = get_answer(prompt)

                # 답변 표시
                answer = result["answer"]
                sources = result["sources"]

                message_placeholder.markdown(answer)

                # 출처 표시
                if sources:
                    with st.expander("📚 참고 문서"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**{i}. {source['title']}**")
                            st.markdown(f"🔗 [{source['source']}]({source['source']})")
                            st.caption(source['content'])
                            if i < len(sources):
                                st.divider()

                # 봇 메시지 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except Exception as e:
                message_placeholder.error(f"❌ 오류 발생: {str(e)}")

                # 에러 메시지 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ 오류가 발생했습니다: {str(e)}"
                })

    # 푸터
    st.divider()
    st.caption("© 2025 동양대학교 AI 도우미 | Powered by AI빅데이터융합")


if __name__ == "__main__":
    main()