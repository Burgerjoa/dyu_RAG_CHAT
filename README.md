# 🎓 동양대학교 AI 도우미 (DYU RAG CHAT)

**22220780 정성우 졸업작품**

RAG(Retrieval-Augmented Generation) 기술을 활용한 동양대학교 학사 정보 챗봇입니다.
학생들의 학사 관련 질문에 정확하고 신속하게 답변합니다.

---

## 📋 목차

- [프로젝트 소개](#-프로젝트-소개)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [프로젝트 구조](#-프로젝트-구조)
- [설치 및 실행](#-설치-및-실행)
- [사용 방법](#-사용-방법)
- [API 문서](#-api-문서)
- [환경 변수](#-환경-변수)
- [개발 가이드](#-개발-가이드)
- [라이선스](#-라이선스)

---

## 🎯 프로젝트 소개

동양대학교 AI 도우미는 RAG(Retrieval-Augmented Generation) 기술을 활용하여 학생들의 다양한 학사 관련 질문에 답변하는 지능형 챗봇 시스템입니다.

### 주요 특징

- **정확한 답변**: 벡터 DB를 통한 의미 기반 검색으로 관련 문서를 찾아 정확한 답변 제공
- **출처 제공**: 모든 답변에 대한 출처 문서를 함께 제공하여 신뢰성 확보
- **사용자 친화적 UI**: Streamlit 기반의 직관적이고 깔끔한 채팅 인터페이스
- **REST API 제공**: FastAPI를 통한 RESTful API로 다양한 클라이언트에서 활용 가능

---

## ✨ 주요 기능

### 1. 학사 정보 질의응답
- 수강신청 일정 안내
- 장학금 신청 방법 안내
- 졸업 요건 확인
- 도서관 이용 안내
- 기숙사 신청 안내
- 기타 학사 관련 질문

### 2. 지능형 검색
- 의미 기반 벡터 검색 (Semantic Search)
- Top-3 관련 문서 자동 검색
- 컨텍스트 기반 답변 생성

### 3. 다양한 인터페이스
- **터미널**: 명령줄 기반 대화형 인터페이스
- **Streamlit**: 웹 기반 채팅 UI
- **REST API**: 프로그래밍 방식 접근

---

## 🛠 기술 스택

### Backend
- **LangChain 0.3.0**: RAG 파이프라인 구축
- **OpenAI API**: GPT-3.5 & Embeddings
- **ChromaDB 0.5.0**: 벡터 데이터베이스
- **FastAPI 0.115.0**: REST API 서버
- **Python 3.11+**: 프로그래밍 언어

### Frontend
- **Streamlit 1.39.0**: 웹 UI 프레임워크
- **Requests**: HTTP 클라이언트

### AI/ML
- **OpenAI GPT-3.5-turbo**: 답변 생성 LLM
- **text-embedding-3-small**: 임베딩 모델
- **Sentence Transformers**: 한국어 임베딩 지원

---

## 📁 프로젝트 구조

```
dyu_RAG_CHAT/
├── .env                      # OpenAI API 키 (보안 주의!)
├── .gitignore               # Git 무시 파일
├── requirements.txt         # Python 패키지 목록
├── README.md               # 프로젝트 문서
├── data/
│   └── sample_data.json    # 학사 정보 샘플 데이터 (5개 문서)
├── vectorstore/            # 벡터 DB 저장소 (자동 생성)
│   └── chroma.sqlite3     # ChromaDB 데이터
├── backend/
│   ├── rag_system.py       # RAG 핵심 로직 구현
│   └── main.py             # FastAPI 서버
└── frontend/
    └── app.py              # Streamlit 웹 UI
```

---

## 🚀 설치 및 실행

### 1. 필수 요구사항

- Python 3.11 이상
- OpenAI API 키
- 가상환경 (권장)

### 2. 저장소 클론

```bash
git clone https://github.com/yourusername/dyu_RAG_CHAT.git
cd dyu_RAG_CHAT
```

### 3. 가상환경 생성 및 활성화

#### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS/Linux
```bash
python -m venv .venv
source .venv/bin/activate
```

### 4. 패키지 설치

```bash
pip install -r requirements.txt
```

### 5. 환경 변수 설정

`.env` 파일에 OpenAI API 키를 설정하세요:

```env
OPENAI_API_KEY=your-actual-api-key-here
```

**주의**: 실제 API 키를 입력하세요. [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급받을 수 있습니다.

### 6. 실행 방법

#### 방법 1: 터미널 인터페이스 (RAG 시스템 단독 실행)

```bash
python backend/rag_system.py
```

대화형 터미널에서 질문을 입력하면 답변을 받을 수 있습니다.

#### 방법 2: FastAPI + Streamlit (웹 UI)

**터미널 1 - FastAPI 서버 실행:**
```bash
cd backend
python main.py
```

**터미널 2 - Streamlit 실행:**
```bash
cd frontend
streamlit run app.py
```

그 다음 브라우저에서 `http://localhost:8501` 접속

#### 방법 3: FastAPI 단독 (API 서버만)

```bash
cd backend
python main.py
```

API 문서는 `http://localhost:8000/docs`에서 확인 가능

---

## 📖 사용 방법

### Streamlit UI 사용

1. FastAPI 서버와 Streamlit을 모두 실행
2. `http://localhost:8501` 접속
3. 채팅 입력창에 질문 입력
4. AI 도우미의 답변 및 출처 확인

### 터미널 사용

```bash
python backend/rag_system.py

질문: 수강신청은 언제야?
# 답변과 출처가 표시됩니다

질문: quit  # 종료
```

### API 직접 호출

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "수강신청은 언제야?"}'
```

---

## 🌐 API 문서

### 엔드포인트

#### 1. `GET /`
헬스 체크

**응답 예시:**
```json
{
  "message": "동양대학교 AI 도우미 API 서버가 정상 작동 중입니다.",
  "status": "healthy",
  "version": "1.0.0"
}
```

#### 2. `POST /chat`
질문에 대한 답변 생성

**요청:**
```json
{
  "question": "수강신청은 언제야?"
}
```

**응답:**
```json
{
  "answer": "2024학년도 1학기 재학생 수강신청은 2월 13일(화)부터 2월 15일(목)까지 진행됩니다...",
  "sources": [
    {
      "title": "2024학년도 1학기 수강신청 안내",
      "source": "https://www.dyu.ac.kr/academic/course-registration",
      "content": "2024학년도 1학기 수강신청 일정을 안내합니다..."
    }
  ]
}
```

#### 3. `GET /health`
상세 헬스 체크

**응답 예시:**
```json
{
  "status": "healthy",
  "rag_system_initialized": true,
  "api_version": "1.0.0"
}
```

### Swagger UI

FastAPI 서버 실행 후 `http://localhost:8000/docs`에서 인터랙티브 API 문서를 확인할 수 있습니다.

---

## 🔐 환경 변수

`.env` 파일에 설정해야 하는 환경 변수:

| 변수명 | 설명 | 필수 여부 |
|--------|------|-----------|
| `OPENAI_API_KEY` | OpenAI API 키 | ✅ 필수 |

**보안 주의사항:**
- `.env` 파일은 절대 Git에 커밋하지 마세요!
- `.gitignore`에 `.env`가 포함되어 있는지 확인하세요
- API 키가 노출되면 즉시 재발급하세요

---

## 👨‍💻 개발 가이드

### 데이터 추가/수정

`data/sample_data.json` 파일을 수정하여 새로운 학사 정보를 추가할 수 있습니다:

```json
[
  {
    "url": "https://www.dyu.ac.kr/...",
    "title": "제목",
    "content": "내용"
  }
]
```

데이터 수정 후 벡터 DB 재생성:
```bash
# vectorstore 폴더 삭제
rm -rf vectorstore/  # Linux/Mac
# 또는
rmdir /s vectorstore  # Windows

# 프로그램 재실행 시 자동으로 새로 생성됨
```

### 모델 변경

`backend/rag_system.py`에서 모델을 변경할 수 있습니다:

```python
# LLM 모델 변경
self.llm = ChatOpenAI(
    model="gpt-4",  # gpt-3.5-turbo → gpt-4
    temperature=0.3
)

# 임베딩 모델 변경
self.embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"  # small → large
)
```

### 청크 크기 조정

`backend/rag_system.py`의 `_create_vectorstore()` 메서드에서:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,    # 청크 크기
    chunk_overlap=100  # 오버랩 크기
)
```

---

## 🧪 테스트 케이스

다음 질문들로 시스템을 테스트해보세요:

1. **수강신청**: "수강신청은 언제야?"
2. **장학금**: "장학금 받으려면 어떻게 해야 돼?"
3. **졸업**: "졸업 학점이 몇 학점이야?"
4. **도서관**: "도서관 운영시간 알려줘"
5. **기숙사**: "기숙사 신청은 어떻게 해?"
6. **정보 없음**: "학식 메뉴 뭐야?" (답변 못함을 정직하게 알려야 함)

---

## 🐛 문제 해결

### 1. OpenAI API 키 오류

```
❌ OPENAI_API_KEY가 .env 파일에 설정되지 않았습니다!
```

**해결 방법**: `.env` 파일에 올바른 API 키를 설정하세요.

### 2. ChromaDB 오류

```
sqlite3.OperationalError: database is locked
```

**해결 방법**: `vectorstore/` 폴더를 삭제하고 재실행하세요.

### 3. API 서버 연결 오류 (Streamlit)

```
❌ API 서버에 연결할 수 없습니다
```

**해결 방법**: FastAPI 서버(`backend/main.py`)가 실행 중인지 확인하세요.

---

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

## 👤 개발자

**정성우** (22220780)
- 동양대학교
- 졸업작품 프로젝트

---

## 🙏 감사의 말

- [LangChain](https://www.langchain.com/) - RAG 프레임워크
- [OpenAI](https://openai.com/) - GPT & Embeddings
- [ChromaDB](https://www.trychroma.com/) - 벡터 데이터베이스
- [FastAPI](https://fastapi.tiangolo.com/) - 웹 프레임워크
- [Streamlit](https://streamlit.io/) - UI 프레임워크

---

**© 2024 동양대학교 AI 도우미 | Powered by LangChain & OpenAI**
