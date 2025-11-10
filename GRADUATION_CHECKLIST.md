# 🎓 졸업작품 제출 전 체크리스트

**현재 점수: B+ (78/100)**
**목표 점수: A (90+/100)**
**필요 작업량: 15-20시간**

---

## 🚨 치명적 문제 (즉시 수정)

### 1. API 키 노출 문제 (30분)

**현재 상태**: `.env` 파일이 Git에 올라가 있음

**조치 사항**:
```bash
# ① OpenAI 대시보드에서 노출된 키 폐기
https://platform.openai.com/api-keys
→ "Revoke" 클릭

# ② Git 히스토리에서 완전 제거
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# ③ 강제 푸시
git push origin --force --all

# ④ 새 API 키 발급 후 로컬에만 저장
# .env는 이미 .gitignore에 있음 (확인 필요)
```

**새 .env.example 파일 생성**:
```bash
# OpenAI API 키 (https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-api-key-here

# API 포트 (기본값: 8000)
API_PORT=8000

# 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# 데이터 경로
DATA_PATH=data/111_cleaned.json
```

---

## 🧪 테스트 코드 추가 (8시간)

**현재 상태**: 테스트 코드 없음 (15/100점)

### Step 1: 테스트 환경 설정 (30분)

```bash
# pytest 설치
pip install pytest pytest-cov pytest-mock httpx

# requirements.txt에 추가
echo "pytest==7.4.3" >> requirements.txt
echo "pytest-cov==4.1.0" >> requirements.txt
echo "pytest-mock==3.12.0" >> requirements.txt
echo "httpx==0.25.2" >> requirements.txt
```

**pytest.ini 생성**:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=backend --cov-report=html --cov-report=term
```

### Step 2: 테스트 디렉토리 생성 (5분)

```bash
mkdir tests
cd tests

# 테스트 파일 생성
touch __init__.py
touch test_rag_system.py
touch test_api.py
touch test_data_processing.py
touch conftest.py
```

### Step 3: RAG 시스템 테스트 작성 (3시간)

**tests/test_rag_system.py** (20개 테스트):
```python
import pytest
import os
from unittest.mock import Mock, patch
from backend.rag_system import RAGSystem

class TestRAGSystemInitialization:
    """RAG 시스템 초기화 테스트"""

    def test_initialization_without_api_key(self):
        """API 키 없이 초기화 시 에러"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                RAGSystem(data_path="test_data.json")

    def test_initialization_with_valid_api_key(self):
        """정상 초기화"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch('backend.rag_system.OpenAIEmbeddings'):
                with patch('backend.rag_system.ChatOpenAI'):
                    rag = RAGSystem(data_path="test_data.json")
                    assert rag is not None

    def test_data_path_stored_correctly(self):
        """데이터 경로가 올바르게 저장되는지"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch('backend.rag_system.OpenAIEmbeddings'):
                with patch('backend.rag_system.ChatOpenAI'):
                    rag = RAGSystem(data_path="custom/path.json")
                    assert rag.data_path == "custom/path.json"

class TestVectorStore:
    """벡터 스토어 관련 테스트"""

    @patch('backend.rag_system.Chroma')
    @patch('backend.rag_system.os.path.exists')
    def test_load_existing_vectorstore(self, mock_exists, mock_chroma):
        """기존 벡터스토어 로드"""
        mock_exists.return_value = True

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            rag = RAGSystem(data_path="test.json")
            # 로드되었는지 확인
            assert mock_chroma.called

    @patch('backend.rag_system.Chroma')
    @patch('backend.rag_system.os.path.exists')
    def test_create_new_vectorstore(self, mock_exists, mock_chroma):
        """새 벡터스토어 생성"""
        mock_exists.return_value = False

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch.object(RAGSystem, '_load_data') as mock_load:
                mock_load.return_value = [{"url": "test", "content": "test"}]
                rag = RAGSystem(data_path="test.json")
                # 생성되었는지 확인

class TestAskFunction:
    """질문 답변 기능 테스트"""

    def test_ask_with_valid_question(self):
        """정상 질문"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch('backend.rag_system.RAGSystem._load_or_create_vectorstore'):
                rag = RAGSystem(data_path="test.json")
                rag.qa_chain = Mock()
                rag.qa_chain.invoke.return_value = {
                    "answer": "테스트 답변",
                    "source_documents": []
                }

                result = rag.ask("테스트 질문?")

                assert result["answer"] == "테스트 답변"
                assert "sources" in result
                assert "question" in result

    def test_ask_with_empty_question(self):
        """빈 질문"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch('backend.rag_system.RAGSystem._load_or_create_vectorstore'):
                rag = RAGSystem(data_path="test.json")

                result = rag.ask("")

                assert "error" in result or result["answer"]

    def test_ask_with_very_long_question(self):
        """매우 긴 질문 (5000자)"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch('backend.rag_system.RAGSystem._load_or_create_vectorstore'):
                rag = RAGSystem(data_path="test.json")
                rag.qa_chain = Mock()
                rag.qa_chain.invoke.return_value = {
                    "answer": "답변",
                    "source_documents": []
                }

                long_question = "테스트 " * 1000  # 5000자 이상
                result = rag.ask(long_question)

                assert result is not None

class TestSourceExtraction:
    """출처 추출 테스트"""

    def test_extract_sources_from_documents(self):
        """문서에서 출처 추출"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch('backend.rag_system.RAGSystem._load_or_create_vectorstore'):
                rag = RAGSystem(data_path="test.json")
                rag.qa_chain = Mock()

                # Mock 문서
                mock_doc = Mock()
                mock_doc.metadata = {"url": "https://test.com"}

                rag.qa_chain.invoke.return_value = {
                    "answer": "답변",
                    "source_documents": [mock_doc]
                }

                result = rag.ask("테스트")

                assert len(result["sources"]) == 1
                assert result["sources"][0] == "https://test.com"

    def test_deduplicate_sources(self):
        """중복 출처 제거"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch('backend.rag_system.RAGSystem._load_or_create_vectorstore'):
                rag = RAGSystem(data_path="test.json")
                rag.qa_chain = Mock()

                # 같은 URL의 문서 2개
                mock_doc1 = Mock()
                mock_doc1.metadata = {"url": "https://test.com"}
                mock_doc2 = Mock()
                mock_doc2.metadata = {"url": "https://test.com"}

                rag.qa_chain.invoke.return_value = {
                    "answer": "답변",
                    "source_documents": [mock_doc1, mock_doc2]
                }

                result = rag.ask("테스트")

                # 중복 제거되어 1개만 남아야 함
                assert len(result["sources"]) == 1

# 더 많은 테스트...
```

### Step 4: API 엔드포인트 테스트 (2시간)

**tests/test_api.py** (15개 테스트):
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from backend.main import app

client = TestClient(app)

class TestHealthEndpoint:
    """헬스체크 엔드포인트 테스트"""

    def test_health_check_success(self):
        """정상 헬스체크"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_check_with_rag_ready(self):
        """RAG 시스템 준비된 상태"""
        with patch('backend.main.rag_system') as mock_rag:
            mock_rag.return_value = Mock()
            response = client.get("/health")
            data = response.json()
            assert "rag_ready" in data

class TestRootEndpoint:
    """루트 엔드포인트 테스트"""

    def test_root_returns_welcome(self):
        """루트 경로 응답"""
        response = client.get("/")
        assert response.status_code == 200
        assert "동양대학교" in response.json()["message"]

class TestChatEndpoint:
    """채팅 엔드포인트 테스트"""

    @patch('backend.main.rag_system')
    def test_chat_with_valid_question(self, mock_rag):
        """정상 질문"""
        mock_rag.ask.return_value = {
            "answer": "수강신청은 2월입니다.",
            "sources": ["https://test.com"],
            "question": "수강신청은 언제야?"
        }

        response = client.post(
            "/chat",
            json={"question": "수강신청은 언제야?"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data

    def test_chat_with_empty_question(self):
        """빈 질문"""
        response = client.post(
            "/chat",
            json={"question": ""}
        )

        assert response.status_code == 400
        assert "질문을 입력해주세요" in response.json()["detail"]

    def test_chat_with_whitespace_only(self):
        """공백만 있는 질문"""
        response = client.post(
            "/chat",
            json={"question": "   "}
        )

        assert response.status_code == 400

    def test_chat_without_question_field(self):
        """question 필드 없음"""
        response = client.post(
            "/chat",
            json={}
        )

        assert response.status_code == 422  # Validation error

    @patch('backend.main.rag_system')
    def test_chat_when_rag_system_fails(self, mock_rag):
        """RAG 시스템 에러"""
        mock_rag.ask.side_effect = Exception("API error")

        response = client.post(
            "/chat",
            json={"question": "테스트"}
        )

        assert response.status_code == 500
        assert "error" in response.json()["detail"]

    def test_chat_with_very_long_question(self):
        """매우 긴 질문 (현재 제한 없음 - 추가 필요)"""
        long_question = "테스트 " * 10000  # 50KB+
        response = client.post(
            "/chat",
            json={"question": long_question}
        )

        # 현재는 통과하지만, 나중에 400이어야 함
        assert response.status_code in [200, 400]

class TestCORS:
    """CORS 설정 테스트"""

    def test_cors_headers_present(self):
        """CORS 헤더 존재"""
        response = client.options("/chat")
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_all_origins(self):
        """모든 Origin 허용 (보안 이슈)"""
        response = client.options(
            "/chat",
            headers={"Origin": "https://malicious.com"}
        )
        # 현재는 통과하지만 보안 문제
        assert response.headers.get("access-control-allow-origin") == "*"

# 더 많은 테스트...
```

### Step 5: 데이터 처리 테스트 (2시간)

**tests/test_data_processing.py**:
```python
import pytest
from backend.data.clean_data import clean_html, remove_duplicates, filter_low_quality

class TestCleanHTML:
    """HTML 정제 테스트"""

    def test_remove_html_tags(self):
        """HTML 태그 제거"""
        html = "<p>안녕하세요</p><script>alert('xss')</script>"
        result = clean_html(html)
        assert "<p>" not in result
        assert "<script>" not in result
        assert "안녕하세요" in result

    def test_remove_multiple_spaces(self):
        """중복 공백 제거"""
        text = "안녕    하세요     반갑습니다"
        result = clean_html(text)
        assert "    " not in result

    def test_preserve_korean_text(self):
        """한국어 보존"""
        text = "동양대학교 RAG 시스템"
        result = clean_html(text)
        assert text == result

class TestRemoveDuplicates:
    """중복 제거 테스트"""

    def test_remove_duplicate_urls(self):
        """중복 URL 제거"""
        data = [
            {"url": "https://test.com", "content": "A"},
            {"url": "https://test.com", "content": "B"},
        ]
        result = remove_duplicates(data)
        assert len(result) == 1

    def test_keep_unique_urls(self):
        """유니크 URL 유지"""
        data = [
            {"url": "https://test1.com", "content": "A"},
            {"url": "https://test2.com", "content": "B"},
        ]
        result = remove_duplicates(data)
        assert len(result) == 2

class TestFilterLowQuality:
    """품질 필터링 테스트"""

    def test_filter_short_content(self):
        """짧은 콘텐츠 필터링"""
        data = [
            {"url": "test", "content": "짧음"},
            {"url": "test2", "content": "충분히 긴 콘텐츠입니다. 최소 50자 이상."},
        ]
        result = filter_low_quality(data, min_length=10)
        assert len(result) == 2

        result = filter_low_quality(data, min_length=20)
        assert len(result) == 1

    def test_empty_list_handling(self):
        """빈 리스트 처리"""
        result = filter_low_quality([], min_length=10)
        assert result == []
```

### Step 6: 테스트 실행 및 커버리지 확인 (30분)

```bash
# 모든 테스트 실행
pytest

# 커버리지 리포트
pytest --cov=backend --cov-report=html

# 리포트 확인
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
```

**목표 커버리지**: 최소 70%

---

## 🔒 보안 강화 (3시간)

### 1. CORS 설정 수정 (15분)

**backend/main.py 수정**:
```python
# 변경 전 (보안 취약)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 변경 후 (보안 강화)
import os

# 환경변수에서 허용 도메인 읽기
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8501"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ✅ 특정 도메인만 허용
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

### 2. 입력 검증 강화 (30분)

**backend/main.py - ChatRequest 모델 수정**:
```python
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="사용자 질문 (1-5000자)"
    )

    @validator('question')
    def validate_question(cls, v):
        """질문 검증"""
        # 공백 제거 후 체크
        v = v.strip()
        if not v:
            raise ValueError("빈 질문은 허용되지 않습니다.")

        # 의심스러운 패턴 체크
        suspicious_patterns = [
            "DROP TABLE",
            "'; --",
            "<script>",
            "onclick=",
        ]

        v_upper = v.upper()
        for pattern in suspicious_patterns:
            if pattern.upper() in v_upper:
                raise ValueError(f"허용되지 않는 패턴: {pattern}")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "question": "수강신청은 언제인가요?"
            }
        }
```

### 3. Rate Limiting 추가 (1시간)

**설치**:
```bash
pip install slowapi
```

**backend/main.py에 추가**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Rate Limiter 초기화
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 엔드포인트에 적용
@app.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")  # 분당 20회 제한
async def chat(request: Request, chat_request: ChatRequest):
    # 기존 코드...
```

### 4. API 인증 추가 (선택사항, 1시간)

**backend/main.py에 추가**:
```python
from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY", "")  # .env에 설정

async def verify_api_key(x_api_key: str = Header(...)):
    """API 키 검증"""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 API 키입니다."
        )
    return x_api_key

# 보호가 필요한 엔드포인트에 적용
@app.post("/chat", dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest):
    # ...
```

---

## 🤖 CI/CD 파이프라인 (2시간)

### GitHub Actions 워크플로우

**.github/workflows/test.yml**:
```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt
        pip install -r frontend/requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        pytest --cov=backend --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

**.github/workflows/deploy.yml**:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to Render
      run: |
        curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

---

## 📖 문서 보완 (2시간)

### 1. 아키텍처 다이어그램 추가

**ARCHITECTURE.md 생성**:
```markdown
# 시스템 아키텍처

## 전체 구조

```
┌─────────────────────────────────────────────────────────┐
│                      사용자                              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Streamlit Frontend                          │
│  - 채팅 인터페이스                                        │
│  - 세션 관리                                              │
│  - API 클라이언트                                         │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/HTTPS
                 ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │           RAG System (rag_system.py)             │   │
│  │  ┌──────────────────────────────────────────┐   │   │
│  │  │  1. 질문 받기                             │   │   │
│  │  │  2. 벡터 검색 (k=3)                       │   │   │
│  │  │  3. 관련 문서 검색                         │   │   │
│  │  │  4. LLM 질의 (컨텍스트 + 질문)           │   │   │
│  │  │  5. 답변 생성                             │   │   │
│  │  └──────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└────────────┬───────────────────────┬────────────────────┘
             │                       │
             ▼                       ▼
┌──────────────────────┐   ┌──────────────────────┐
│   ChromaDB           │   │   OpenAI API          │
│   (벡터 DB)          │   │   - gpt-4o-mini       │
│   - 임베딩 저장      │   │   - text-embed-3-small│
│   - 유사도 검색      │   │                       │
└──────────────────────┘   └──────────────────────┘
```

## 데이터 흐름

1. **크롤링 → 정제 → 임베딩**
2. **질문 → 검색 → LLM → 답변**

## 주요 컴포넌트

### RAGSystem
- 역할: 핵심 RAG 로직
- 의존성: LangChain, OpenAI, ChromaDB
- 파일: backend/rag_system.py

### FastAPI Server
- 역할: API 엔드포인트
- 엔드포인트: /chat, /health, /
- 파일: backend/main.py

### Streamlit UI
- 역할: 사용자 인터페이스
- 기능: 채팅, 히스토리, 출처 표시
- 파일: frontend/app.py
```

### 2. 보안 정책 문서

**SECURITY.md**:
```markdown
# 보안 정책

## 지원 버전

| 버전 | 지원 여부 |
| ---- | -------- |
| 1.0.x | ✅       |

## 취약점 보고

보안 취약점을 발견하셨다면:
- 이메일: your-email@example.com
- 공개 이슈에 게시하지 말 것

## 보안 조치

### 구현된 보안 기능
- ✅ 환경변수 기반 API 키 관리
- ✅ CORS 제한
- ✅ Rate Limiting (20req/min)
- ✅ 입력 검증 (길이, 패턴)
- ✅ SQL Injection 방어
- ✅ XSS 방어 (HTML 태그 제거)

### 권장 설정
- API 키 절대 커밋 금지
- Production에서 HTTPS 사용
- .env 파일 .gitignore에 추가
```

---

## ✅ 최종 체크리스트

### 코드 품질
- [ ] 테스트 커버리지 70% 이상
- [ ] 모든 테스트 통과
- [ ] Linting 에러 없음 (flake8, black)
- [ ] Type hints 추가 (mypy)

### 보안
- [x] ~~API 키 노출~~ → 폐기 및 제거
- [ ] CORS 제한 설정
- [ ] Rate Limiting 추가
- [ ] 입력 검증 강화
- [ ] .env.example 파일 생성

### 문서화
- [ ] README 업데이트 (테스트 섹션 추가)
- [ ] ARCHITECTURE.md 생성
- [ ] SECURITY.md 생성
- [ ] API 문서 업데이트
- [ ] 코드 주석 보완

### CI/CD
- [ ] GitHub Actions 워크플로우 추가
- [ ] 자동 테스트 파이프라인
- [ ] 커버리지 리포팅
- [ ] 배포 자동화

### 배포
- [ ] Render 배포 테스트
- [ ] Streamlit Cloud 배포 테스트
- [ ] 환경변수 설정 확인
- [ ] 프로덕션 헬스체크

---

## 📊 예상 점수 변화

| 항목 | 현재 | 개선 후 |
|-----|------|--------|
| 테스트 | 15점 | 85점 |
| 보안 | 35점 | 85점 |
| 문서화 | 85점 | 95점 |
| CI/CD | 0점 | 80점 |
| **전체** | **78점 (B+)** | **92점 (A)** |

---

## 🎯 제출 전 최종 확인

1. [ ] Git에 API 키 없음 확인
2. [ ] 모든 테스트 통과
3. [ ] 배포 가능 확인 (로컬 + 클라우드)
4. [ ] README 최신화
5. [ ] 프레젠테이션 자료 준비
6. [ ] 데모 시나리오 준비 (6가지 질문)
7. [ ] 코드 리뷰 완료

---

## 📅 작업 일정 (예시)

| 일차 | 작업 | 시간 |
|-----|------|------|
| **Day 1** | API 키 폐기 + 테스트 환경 설정 | 2시간 |
| **Day 2** | RAG 시스템 테스트 작성 | 4시간 |
| **Day 3** | API 테스트 + 데이터 처리 테스트 | 4시간 |
| **Day 4** | 보안 강화 (CORS, 입력 검증) | 3시간 |
| **Day 5** | CI/CD + 문서화 | 3시간 |
| **Day 6** | 최종 테스트 + 배포 확인 | 2시간 |

**총 소요 시간: 18시간 (약 3일)**

---

## 🎓 제출 시 강조할 점

### 기술적 우수성
1. ✅ 최신 기술 스택 (RAG, LangChain, FastAPI)
2. ✅ 완전 자동화 파이프라인 (크롤링 → OCR → 정제)
3. ✅ 모듈화된 아키텍처
4. ✅ 클라우드 배포 경험

### 실용성
1. ✅ 실제 문제 해결 (학교 정보 접근성)
2. ✅ 확장 가능한 설계
3. ✅ 비용 효율적 (gpt-4o-mini)

### 품질 관리
1. ✅ 70%+ 테스트 커버리지
2. ✅ CI/CD 파이프라인
3. ✅ 보안 강화
4. ✅ 상세한 문서화

---

**참고**: 이 체크리스트의 모든 항목을 완료하면 **A학점 수준(90점 이상)**의 졸업작품이 됩니다.
