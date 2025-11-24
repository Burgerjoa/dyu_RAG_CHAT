"""
동양대학교 RAG 챗봇 FastAPI 백엔드

이 모듈은 RAG 시스템을 REST API로 제공합니다.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any
import sys
import os

# backend 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_system import RAGSystem

# FastAPI 앱 생성
app = FastAPI(
    title="동양대학교 AI 도우미 API",
    description="RAG 기반 학사 정보 챗봇 API",
    version="1.0.0"
)

# CORS 설정 (모든 origin 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 RAG 시스템 인스턴스
rag_system: RAGSystem = None


# Request/Response 모델
class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    question: str

    class Config:
        json_schema_extra = {
            "example": {
                "question": "수강신청은 언제야?"
            }
        }


class Source(BaseModel):
    """출처 문서 모델"""
    title: str
    source: str
    content: str


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    answer: str
    sources: List[Source]

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "수강신청은 2월 13일부터 15일까지입니다.",
                "sources": [
                    {
                        "title": "2024학년도 1학기 수강신청 안내",
                        "source": "https://www.dyu.ac.kr/academic/course-registration",
                        "content": "2024학년도 1학기 수강신청 일정을 안내합니다..."
                    }
                ]
            }
        }


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 RAG 시스템 초기화"""
    global rag_system
    try:
        print("=" * 60)
        print("🚀 FastAPI 서버를 시작합니다...")
        print("=" * 60)
        rag_system = RAGSystem(data_path="data/111_cleaned.json")
        print("✅ FastAPI 서버가 준비되었습니다!")
        print("=" * 60)
    except Exception as e:
        print(f"❌ RAG 시스템 초기화 실패: {e}")
        raise


@app.get("/", tags=["Health Check"])
async def root() -> Dict[str, str]:
    """
    헬스 체크 엔드포인트

    Returns:
        서버 상태 메시지
    """
    return {
        "message": "동양대학교 AI 도우미 API 서버가 정상 작동 중입니다.",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    채팅 API - 질문에 대한 답변 생성

    Args:
        request: 사용자 질문을 포함한 요청

    Returns:
        답변과 출처를 포함한 응답

    Raises:
        HTTPException: RAG 시스템 미초기화 또는 처리 중 오류 발생 시
    """
    # RAG 시스템 초기화 확인
    if rag_system is None:
        raise HTTPException(
            status_code=500,
            detail="RAG 시스템이 초기화되지 않았습니다."
        )

    # 질문 유효성 검사
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="질문을 입력해주세요."
        )

    try:
        # 답변 생성
        result = rag_system.ask(request.question)

        # 응답 반환
        return ChatResponse(
            answer=result['answer'],
            sources=[Source(**source) for source in result['sources']]
        )

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"답변 생성 중 오류가 발생했습니다: {str(e)}"
        )


@app.get("/health", tags=["Health Check"])
async def health_check() -> Dict[str, Any]:
    """
    상세 헬스 체크 엔드포인트

    Returns:
        서버 및 RAG 시스템 상태
    """
    return {
        "status": "healthy",
        "rag_system_initialized": rag_system is not None,
        "api_version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn

    print("🌐 FastAPI 서버를 시작합니다...")
    print("📍 서버 주소: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )