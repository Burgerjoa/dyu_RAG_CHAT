# DYU RAG Chat

> RAG-based university information chatbot that retrieves school-related documents and generates grounded answers with sources.

DYU RAG Chat은 동양대학교 학사 정보를 기반으로 학생의 질문에 답변하는 RAG 챗봇입니다.  
단순히 LLM에게 질문을 던지는 방식이 아니라, 학사 관련 문서를 벡터 검색으로 먼저 찾고, 검색된 문서를 근거로 답변을 생성하도록 구성했습니다.

이 프로젝트는 졸업작품으로 시작했지만, 핵심 목표는 **문서 검색 기반 질의응답 시스템의 전체 흐름을 직접 구현해보는 것**이었습니다.

## 핵심 기능

- 학사 정보 기반 질의응답
- ChromaDB를 활용한 벡터 검색
- 검색된 문서를 기반으로 한 답변 생성
- 답변 출처 제공
- FastAPI 기반 REST API
- Streamlit 기반 웹 채팅 UI
- 터미널 기반 테스트 인터페이스

## Tech Stack

| Area | Stack |
|---|---|
| Language | Python |
| Backend | FastAPI |
| UI | Streamlit |
| LLM | OpenAI GPT |
| Embedding | OpenAI Embeddings / Sentence Transformers |
| Vector DB | ChromaDB |
| RAG Framework | LangChain |

## Architecture

```text
User Question
    ↓
FastAPI / Streamlit UI
    ↓
Query Embedding
    ↓
ChromaDB Vector Search
    ↓
Relevant Documents
    ↓
LLM Answer Generation
    ↓
Answer + Sources
```

## Why I Built This

학교 홈페이지나 공지사항에 흩어져 있는 학사 정보는 사용자가 직접 찾아야 하는 경우가 많습니다.  
이 프로젝트는 사용자가 자연어로 질문하면, 관련 문서를 검색하고 그 근거를 바탕으로 답변하는 챗봇을 만드는 것을 목표로 했습니다.

특히 RAG 구조를 직접 구현하면서 다음 흐름을 학습했습니다.

- 문서 데이터를 수집하고 정리하는 과정
- 텍스트를 임베딩하여 벡터 DB에 저장하는 과정
- 사용자 질문과 관련도 높은 문서를 검색하는 과정
- 검색 결과를 LLM 프롬프트에 컨텍스트로 주입하는 과정
- 답변과 출처를 함께 제공하는 방식

## Main Features

### 1. Document-based Question Answering

사용자의 질문에 대해 LLM이 바로 답변하지 않고, 먼저 관련 문서를 검색한 뒤 답변을 생성합니다.

예시 질문:

```text
수강신청은 언제야?
장학금 신청은 어떻게 해?
졸업 요건 알려줘
도서관 운영시간 알려줘
```

### 2. Semantic Search

문서 키워드가 정확히 일치하지 않아도 의미적으로 관련 있는 문서를 찾을 수 있도록 벡터 검색을 사용했습니다.

```text
Question → Embedding → Vector Search → Top-k Documents
```

### 3. Source-grounded Answers

답변 생성 시 검색된 문서를 함께 사용하여, 가능한 한 근거 기반 답변을 제공하도록 구성했습니다.

### 4. Multiple Interfaces

| Interface | Description |
|---|---|
| Terminal | RAG 시스템을 빠르게 테스트하는 CLI 방식 |
| FastAPI | 외부 클라이언트와 연결 가능한 REST API |
| Streamlit | 사용자가 직접 질문할 수 있는 웹 채팅 UI |

## Project Structure

```text
dyu_RAG_CHAT/
├── backend/
│   ├── rag_system.py       # RAG 핵심 로직
│   └── main.py             # FastAPI 서버
├── frontend/
│   └── app.py              # Streamlit UI
├── data/
│   └── sample_data.json    # 학사 정보 샘플 데이터
├── requirements.txt
├── .env.example
└── README.md
```

## What I Learned

이 프로젝트를 통해 단순히 LLM API를 호출하는 것과 RAG 시스템을 구성하는 것은 다르다는 점을 경험했습니다.

특히 다음 부분을 직접 다뤘습니다.

- 문서 데이터 구조 설계
- 임베딩 모델 사용
- ChromaDB를 활용한 벡터 검색
- 검색 결과를 프롬프트 컨텍스트로 조합
- FastAPI와 Streamlit을 분리한 구조
- API 응답에 답변과 출처를 함께 포함하는 방식

## Troubleshooting

### 1. 검색 결과 품질 문제

처음에는 질문과 관련 없는 문서가 검색되는 경우가 있었습니다.  
이를 줄이기 위해 문서 단위를 너무 크게 두지 않고, 청크 크기와 overlap을 조정하면서 검색 결과의 품질을 개선했습니다.

### 2. 답변의 신뢰성 문제

LLM이 검색된 문서와 관계없는 내용을 생성할 수 있기 때문에, 답변 생성 시 검색된 문서를 컨텍스트로 제공하고 출처 정보를 함께 보여주는 방향으로 구성했습니다.

### 3. API 서버와 UI 분리

처음에는 RAG 로직과 UI가 강하게 섞일 수 있었지만, FastAPI 백엔드와 Streamlit 프론트엔드를 분리하여 API 기반 구조로 정리했습니다.

## Getting Started

### 1. Clone

```bash
git clone https://github.com/Burgerjoa/dyu_RAG_CHAT.git
cd dyu_RAG_CHAT
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

`.env` 파일을 생성하고 OpenAI API 키를 설정합니다.

```env
OPENAI_API_KEY=your_openai_api_key
```

### 5. Run FastAPI Server

```bash
cd backend
python main.py
```

API 문서:

```text
http://localhost:8000/docs
```

### 6. Run Streamlit UI

새 터미널에서 실행합니다.

```bash
cd frontend
streamlit run app.py
```

접속:

```text
http://localhost:8501
```

## API Example

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "수강신청은 언제야?"}'
```

Response example:

```json
{
  "answer": "검색된 학사 정보 문서를 바탕으로 생성된 답변입니다.",
  "sources": [
    {
      "title": "수강신청 안내",
      "source": "https://www.dyu.ac.kr/...",
      "content": "관련 문서 내용..."
    }
  ]
}
```

## Future Improvements

- 실제 학사 공지 데이터 자동 업데이트
- 관리자용 문서 업로드 기능
- 답변 신뢰도 점수 표시
- 사용자 피드백 기반 검색 품질 개선
- 배포 환경 구성
- 한국어 임베딩 모델 비교 실험

## Note

이 프로젝트는 학습 및 졸업작품 목적으로 제작되었습니다.  
실제 학사 정보는 반드시 학교 공식 홈페이지와 공지사항을 확인해야 합니다.
