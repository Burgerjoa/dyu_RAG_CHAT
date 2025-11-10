# 프로젝트 개선 방안

## 우선순위별 개선 과제

---

## 🔥 HIGH Priority (즉시 개선 가능)

### 1. **데이터 품질 개선** ⭐⭐⭐⭐⭐

#### 현재 문제
- 크롤링 데이터가 웹사이트 전체 HTML 포함
- 불필요한 메뉴, 푸터, 네비게이션 텍스트 포함
- 중복 데이터 (같은 URL이 여러 번)

#### 개선 방법
```python
# data/clean_data.py 생성
import json
from bs4 import BeautifulSoup

def clean_html(content):
    """HTML 태그 제거 및 텍스트 정제"""
    soup = BeautifulSoup(content, 'html.parser')

    # 불필요한 태그 제거
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()

    text = soup.get_text()

    # 중복 공백 제거
    lines = [line.strip() for line in text.splitlines()]
    text = '\n'.join(line for line in lines if line)

    return text

def remove_duplicates(data):
    """URL 기준 중복 제거"""
    seen = set()
    unique = []
    for item in data:
        if item['url'] not in seen:
            seen.add(item['url'])
            unique.append(item)
    return unique

# 실행
with open('111.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 중복 제거
data = remove_duplicates(data)
print(f"중복 제거 후: {len(data)}개")

# HTML 정제
for item in data:
    item['content'] = clean_html(item['content'])

# 저장
with open('111_cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

**예상 효과:**
- 벡터 DB 크기 50% 감소
- 검색 정확도 30% 향상
- 답변 품질 대폭 개선

---

### 2. **청크 크기 최적화**

#### 현재 설정
```python
chunk_size=500
chunk_overlap=100
```

#### 개선안
```python
# backend/rag_system.py
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,           # 500 → 800 (더 많은 맥락)
    chunk_overlap=200,        # 100 → 200 (연속성 향상)
    separators=["\n\n", "\n", ". ", " ", ""],  # 구분자 명시
    length_function=len
)
```

**테스트 방법:**
- chunk_size: 400, 600, 800, 1000 테스트
- 각각의 답변 품질 비교

---

### 3. **검색 개수 조정**

#### 현재 설정
```python
search_kwargs={"k": 3}  # Top-3
```

#### 개선안
```python
# A. 더 많은 문서 검색
search_kwargs={"k": 5}  # Top-5

# B. 유사도 임계값 설정
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 5,
        "score_threshold": 0.7  # 70% 이상 유사한 것만
    }
)
```

---

### 4. **프롬프트 엔지니어링 개선**

#### 현재 프롬프트
```python
template = """당신은 동양대학교의 친절한 AI 도우미입니다.
학생들의 학사 관련 질문에 정확하고 친절하게 답변해주세요.
..."""
```

#### 개선안
```python
template = """당신은 동양대학교의 전문 학사 상담 AI입니다.

## 역할
- 학생들의 학사 관련 질문에 정확하고 구체적으로 답변
- 공식적이면서도 친근한 톤 유지

## 답변 규칙
1. **정확성 우선**: 주어진 정보만 사용, 추측 금지
2. **구조화된 답변**:
   - 핵심 답변 먼저
   - 세부 사항은 항목별로
   - 날짜/시간/장소는 명확히 표시
3. **추가 정보 제공**:
   - 관련 부서 연락처
   - 참고 웹사이트 링크
   - 주의사항이 있다면 강조
4. **정보 부족 시**: 어떤 부서에 문의하면 되는지 안내

## 예시
질문: "수강신청은 언제야?"
좋은 답변:
"📅 2025학년도 1학기 수강신청 일정은 다음과 같습니다:

• 재학생: 2025년 2월 13일(목) ~ 15일(토)
• 신입생: 2025년 2월 20일(목)

📞 문의: 학사지원팀 (054-630-1234)
🔗 자세한 내용: https://www.dyu.ac.kr/academic/..."

나쁜 답변:
"학사 공지를 확인하세요."

---

참고 정보:
{context}

질문: {question}

답변:"""
```

---

## 🟡 MEDIUM Priority (1-2주 내 개선)

### 5. **하이브리드 검색 (BM25 + Vector)**

#### 개념
- **Vector 검색**: 의미적 유사도 (현재 사용 중)
- **BM25 검색**: 키워드 매칭
- **하이브리드**: 둘을 결합

#### 구현
```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# BM25 retriever
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 3

# Vector retriever (기존)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 앙상블 (가중 평균)
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.3, 0.7]  # BM25 30%, Vector 70%
)
```

**예상 효과:**
- "수강신청" 같은 명확한 키워드 검색 정확도 향상
- 오타나 유사 표현에도 강건

---

### 6. **Reranking 추가**

#### 개념
검색된 문서를 다시 정렬하여 가장 관련성 높은 것만 선택

#### 구현
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Reranker 설정
compressor = LLMChainExtractor.from_llm(self.llm)

# Compression retriever
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_retriever
)
```

**비용:** 추가 LLM 호출로 비용 증가 (~2배)

---

### 7. **대화 기록 추가 (Chat History)**

#### 현재 문제
각 질문이 독립적 → 이전 질문 맥락 없음

#### 개선안
```python
from langchain.chains import ConversationalRetrievalChain

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=self.llm,
    retriever=self.vectorstore.as_retriever(),
    return_source_documents=True,
    verbose=True
)

# 대화 기록 포함
chat_history = []
result = qa_chain({
    "question": question,
    "chat_history": chat_history
})
chat_history.append((question, result["answer"]))
```

**예시:**
```
사용자: "수강신청은 언제야?"
AI: "2월 13일입니다."
사용자: "그날 몇 시부터야?" ← 맥락 이해!
AI: "오전 10시부터입니다."
```

---

### 8. **캐싱 시스템**

#### 목적
동일 질문 반복 시 OpenAI API 호출 줄이기

#### 구현
```python
from functools import lru_cache
import hashlib

class RAGSystemWithCache:
    def __init__(self):
        self.cache = {}

    def ask(self, question: str):
        # 질문 해시
        q_hash = hashlib.md5(question.encode()).hexdigest()

        # 캐시 확인
        if q_hash in self.cache:
            print("🔄 캐시에서 답변 반환")
            return self.cache[q_hash]

        # 새 답변 생성
        result = self.qa_chain.invoke({"query": question})

        # 캐시 저장
        self.cache[q_hash] = result

        return result
```

**예상 효과:**
- 비용 50% 절감 (인기 질문)
- 응답 속도 10배 향상

---

## 🔵 LOW Priority (장기 과제)

### 9. **파인튜닝** ⭐⭐⭐

#### A. Embedding 모델 파인튜닝

**목적:** 동양대 특화 용어 이해 향상

**방법:**
```python
# 학습 데이터 준비
training_data = [
    {
        "query": "수강신청",
        "positive": ["2025학년도 1학기 수강신청 안내..."],
        "negative": ["동아리 신청 안내..."]
    },
    # ... 100개 이상
]

# OpenAI Embedding Fine-tuning
# https://platform.openai.com/docs/guides/embeddings/use-cases
```

**비용:** ~$100-500 (1회)
**효과:** 검색 정확도 20-30% 향상

#### B. GPT 파인튜닝

**목적:** 동양대 답변 스타일 학습

**방법:**
```python
# 학습 데이터 (JSONL 형식)
{"messages": [
    {"role": "system", "content": "당신은 동양대 AI 도우미입니다."},
    {"role": "user", "content": "수강신청은 언제야?"},
    {"role": "assistant", "content": "📅 2025학년도 1학기 수강신청..."}
]}
# ... 100개 이상
```

**비용:** ~$50-200 (1회) + 추론 비용 증가
**효과:** 답변 일관성 향상

**결론:** RAG가 잘 작동한다면 **파인튜닝 불필요**

---

### 10. **다국어 지원**

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# 언어 감지 및 번역
detector = LanguageDetector()
translator = Translator()

if detector.detect(question) == 'en':
    question_ko = translator.translate(question, dest='ko')
    answer = rag.ask(question_ko)
    answer_en = translator.translate(answer, dest='en')
    return answer_en
```

---

### 11. **음성 인터페이스**

```python
# Whisper (음성 → 텍스트)
import openai

audio_file = open("question.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)

# RAG 처리
answer = rag.ask(transcript.text)

# TTS (텍스트 → 음성)
speech = openai.Audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=answer
)
```

---

### 12. **평가 시스템 구축**

#### 자동 평가
```python
# test/evaluation.py
test_cases = [
    {
        "question": "수강신청은 언제야?",
        "expected_keywords": ["2월", "13일", "재학생"],
        "should_not_contain": ["모르겠습니다"]
    },
    # ... 50개 이상
]

def evaluate_rag(rag_system, test_cases):
    scores = []
    for test in test_cases:
        result = rag_system.ask(test["question"])
        score = calculate_score(result, test)
        scores.append(score)

    return {
        "average": sum(scores) / len(scores),
        "pass_rate": sum(1 for s in scores if s > 0.7) / len(scores)
    }
```

---

## 📊 추천 개선 순서

### Phase 1: 데이터 품질 (1주)
1. ✅ 데이터 중복 제거
2. ✅ HTML 정제
3. ✅ 청크 크기 실험

**예상 효과:** 답변 품질 50% 향상

### Phase 2: 검색 개선 (1-2주)
4. ✅ 프롬프트 개선
5. ✅ 하이브리드 검색
6. ✅ Top-K 조정

**예상 효과:** 검색 정확도 30% 향상

### Phase 3: 사용자 경험 (2주)
7. ✅ 대화 기록
8. ✅ 캐싱
9. ✅ 평가 시스템

**예상 효과:** 비용 50% 절감, UX 개선

### Phase 4: 고급 기능 (1개월+)
10. ⏳ 파인튜닝 (필요시)
11. ⏳ 다국어/음성

---

## 💰 비용 vs 효과 분석

| 개선 사항 | 개발 시간 | 비용 | 효과 | 추천도 |
|---------|---------|------|------|--------|
| 데이터 정제 | 1일 | 무료 | ⭐⭐⭐⭐⭐ | 필수 |
| 청크 최적화 | 3시간 | 무료 | ⭐⭐⭐⭐ | 필수 |
| 프롬프트 개선 | 2시간 | 무료 | ⭐⭐⭐⭐ | 필수 |
| 하이브리드 검색 | 1일 | 무료 | ⭐⭐⭐ | 권장 |
| Reranking | 1일 | API 비용↑ | ⭐⭐⭐ | 선택 |
| 대화 기록 | 2일 | 무료 | ⭐⭐⭐⭐ | 권장 |
| 캐싱 | 1일 | 무료 | ⭐⭐⭐⭐⭐ | 권장 |
| 파인튜닝 | 1주 | $100-500 | ⭐⭐ | 비추천* |
| 다국어 | 3일 | API 비용↑ | ⭐⭐ | 선택 |
| 음성 | 2일 | API 비용↑ | ⭐⭐ | 선택 |

*RAG가 잘 작동한다면 파인튜닝 불필요

---

## 🎯 당장 시작할 수 있는 개선

### 오늘 바로 (30분)
```python
# 1. Top-K 조정
search_kwargs={"k": 5}  # 3 → 5

# 2. Temperature 조정
temperature=0.1  # 0.3 → 0.1 (더 일관된 답변)

# 3. 청크 크기 증가
chunk_size=800  # 500 → 800
```

### 이번 주 (1-2일)
1. 데이터 중복 제거 스크립트 작성
2. 프롬프트 개선
3. 간단한 캐싱 추가

---

어떤 개선부터 시작하고 싶으신가요? 코드 작성을 도와드릴게요!
