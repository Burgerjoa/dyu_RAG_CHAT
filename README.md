# DYU RAG Chat

> 학교 정보를 문서 기반으로 검색하고 답변하는 RAG 챗봇

DYU RAG Chat은 학교 공지, 학사 정보, 문서 데이터를 기반으로 질문에 답하는 RAG 시스템이다.

LLM이 기억에 의존해 답하게 두지 않고, 먼저 관련 문서를 검색한 뒤 그 내용을 바탕으로 답변을 생성한다.

```text
질문 입력 → 문서 검색 → 관련 문서 추출 → 답변 생성 → 출처 제공
```

## 주요 기능

- 학사 정보 기반 질의응답
- 문서 임베딩
- ChromaDB 기반 벡터 검색
- 검색 결과 기반 답변 생성
- 답변 출처 제공
- FastAPI 서버
- Streamlit 채팅 UI

## 기술 스택

| 영역 | 기술 |
|---|---|
| Language | Python |
| Backend | FastAPI |
| UI | Streamlit |
| Vector DB | ChromaDB |
| LLM | OpenAI API |
| RAG | LangChain |
| Embedding | OpenAI Embeddings / Sentence Transformers |

## 동작 구조

```text
User Question
    ↓
Embedding
    ↓
ChromaDB Vector Search
    ↓
Relevant Documents
    ↓
Prompt Construction
    ↓
LLM Answer Generation
    ↓
Answer + Sources
```

## 왜 RAG인가

학교 정보는 공지사항, 학사 문서, 홈페이지, PDF 등에 흩어져 있다.

일반적인 챗봇은 이런 정보를 정확히 알지 못한다.  
그래서 DYU RAG Chat은 질문을 받으면 먼저 관련 문서를 검색하고, 검색된 문서를 근거로 답변을 생성한다.

핵심은 “그럴듯한 답변”이 아니라, **검색된 문서에 기반한 답변**이다.

## 시스템 구성

### 1. 문서 처리

학사 정보 데이터를 수집하고, 검색 가능한 단위로 나눈다.  
문서가 너무 크면 검색 정확도가 떨어지고, 너무 작으면 문맥이 부족해진다.

그래서 문서 단위를 조정하면서 질문과 관련 있는 정보가 잘 검색되도록 구성한다.

### 2. 벡터 검색

사용자 질문을 임베딩으로 변환하고, ChromaDB에서 의미적으로 가까운 문서를 검색한다.

```text
question → embedding → vector search → top-k documents
```

### 3. 답변 생성

검색된 문서를 프롬프트 컨텍스트로 넣고, LLM이 해당 내용을 기반으로 답변을 생성한다.

답변에는 가능한 한 출처 정보를 함께 포함한다.

## API 예시

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "수강신청은 언제야?"}'
```

응답 예시:

```json
{
  "answer": "검색된 학사 정보 문서를 기반으로 생성된 답변입니다.",
  "sources": [
    {
      "title": "수강신청 안내",
      "content": "관련 문서 내용..."
    }
  ]
}
```

## 실행 방법

```bash
git clone https://github.com/Burgerjoa/dyu_RAG_CHAT.git
cd dyu_RAG_CHAT
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

```bash
pip install -r requirements.txt
```

`.env` 파일 생성:

```env
OPENAI_API_KEY=your_openai_api_key
```

FastAPI 실행:

```bash
cd backend
python main.py
```

Streamlit 실행:

```bash
cd frontend
streamlit run app.py
```

## 설계 메모

### 검색 품질

RAG에서 답변 품질은 모델보다 검색 결과에 크게 좌우된다.

초기에는 질문과 직접 관련 없는 문서가 검색되는 문제가 있었고, 문서 청크 단위와 검색 개수를 조정하면서 검색 품질을 개선했다.

### 출처 기반 답변

LLM은 검색된 문서에 없는 내용도 생성할 수 있다.  
이를 줄이기 위해 답변 생성 시 검색된 문서를 컨텍스트로 제공하고, 사용자에게 출처 정보를 함께 보여주는 구조로 만들었다.

### API와 UI 분리

RAG 로직을 Streamlit 안에 모두 넣지 않고, FastAPI 서버와 Streamlit UI를 분리했다.

이 구조는 나중에 웹 프론트엔드, 모바일 앱, 다른 클라이언트가 붙기 쉬운 형태다.

## 제한사항

- 실제 학사 정보는 학교 공식 공지를 확인해야 한다.
- 문서 데이터가 최신이 아니면 답변도 부정확할 수 있다.
- 검색 결과가 부정확하면 답변 품질도 떨어질 수 있다.

## 개선 예정

- 학사 공지 자동 수집
- 문서 업로드 관리자 페이지
- 답변 신뢰도 표시
- 사용자 피드백 기반 검색 개선
- 한국어 임베딩 모델 비교
- 배포 환경 구성
