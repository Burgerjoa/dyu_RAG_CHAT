# 임베딩 모델 비교 가이드

## OpenAI 임베딩 모델 비교

### 1. **text-embedding-3-small** (현재 사용 중) ⭐⭐⭐⭐

**스펙:**
- 차원: 1,536
- 최대 토큰: 8,191
- 비용: **$0.02 / 1M 토큰**

**장점:**
- ✅ 매우 저렴
- ✅ 빠른 속도
- ✅ 한국어 성능 우수
- ✅ 최신 모델 (2024년)

**단점:**
- ⚠️ large보다 정확도 약간 낮음

**추천 대상:**
- 대부분의 경우 (가성비 최고)
- 학생 프로젝트 ⭐

---

### 2. **text-embedding-3-large** ⭐⭐⭐⭐⭐

**스펙:**
- 차원: 3,072 (2배!)
- 최대 토큰: 8,191
- 비용: **$0.13 / 1M 토큰** (6.5배 비쌈)

**장점:**
- ✅ 최고 정확도
- ✅ 복잡한 쿼리에 강함
- ✅ 한국어 성능 최상

**단점:**
- ❌ 비용 6.5배
- ❌ 벡터 DB 크기 2배
- ❌ 검색 속도 느림

**추천 대상:**
- 정확도가 중요한 프로덕션
- 복잡한 질문 처리

---

### 3. **text-embedding-ada-002** (구버전)

**스펙:**
- 차원: 1,536
- 비용: **$0.10 / 1M 토큰**

**상태:**
- ⚠️ 레거시 모델
- text-embedding-3-small로 교체 권장

---

## 성능 비교 (MTEB Benchmark)

| 모델 | 영어 성능 | 한국어 성능 | 비용 | 속도 | 종합 |
|------|----------|------------|------|------|------|
| **text-embedding-3-large** | 64.6% | ~62% | $$$$ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **text-embedding-3-small** | 62.3% | ~60% | $ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **text-embedding-ada-002** | 61.0% | ~58% | $$ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**차이:**
- large vs small: 정확도 약 **3-5% 향상**
- 체감 차이: **미미함** (대부분의 경우)

---

## 무료 오픈소스 대안

### 1. **multilingual-e5-large** (Microsoft)

**스펙:**
- 차원: 1,024
- 비용: **무료!**
- 한국어 성능: ⭐⭐⭐⭐

**장점:**
- ✅ 완전 무료
- ✅ 로컬 실행 가능
- ✅ 다국어 지원 우수

**단점:**
- ❌ OpenAI보다 성능 낮음 (~5-10%)
- ❌ 로컬에서 GPU 필요 (느림)
- ❌ 설정 복잡

**구현:**
```python
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large",
    model_kwargs={'device': 'cpu'}  # 또는 'cuda'
)
```

---

### 2. **paraphrase-multilingual-mpnet-base-v2**

**스펙:**
- 차원: 768
- 비용: **무료!**
- 한국어 성능: ⭐⭐⭐

**장점:**
- ✅ 무료
- ✅ CPU에서도 빠름
- ✅ 가벼움

**단점:**
- ❌ 성능 보통
- ❌ 긴 텍스트에 약함 (512 토큰 제한)

---

### 3. **KoSimCSE** (한국어 특화) ⭐⭐⭐⭐

**스펙:**
- 차원: 768
- 비용: **무료!**
- 한국어 성능: ⭐⭐⭐⭐⭐ (한국어 최고!)

**장점:**
- ✅ 무료
- ✅ **한국어 특화**
- ✅ 국내 데이터로 학습

**단점:**
- ❌ 영어 성능 낮음
- ❌ 영어 질문 안 됨

**구현:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BM-K/KoSimCSE-roberta')
embeddings = HuggingFaceEmbeddings(
    model_name="BM-K/KoSimCSE-roberta"
)
```

---

## 실전 비용 계산

### 동양대 프로젝트 예상 비용

**데이터:**
- 문서 수: 2,712개 (정제 후)
- 평균 길이: 320자
- 총 토큰: ~2,712 × 320 / 4 ≈ **217,000 토큰**

**임베딩 생성 비용 (1회):**

| 모델 | 비용 |
|------|------|
| text-embedding-3-small | $0.02 × 0.217 = **$0.004** |
| text-embedding-3-large | $0.13 × 0.217 = **$0.028** |
| 무료 모델 | **$0** |

**⚠️ 질문 임베딩은 거의 공짜 (질문당 0.0001원 수준)**

---

## 내 프로젝트에 맞는 선택

### 시나리오 1: **학생 프로젝트 (현재)** ✅
→ **text-embedding-3-small**

**이유:**
- 비용 거의 없음 ($0.004)
- 성능 충분
- 빠름

---

### 시나리오 2: **최고 성능 필요**
→ **text-embedding-3-large**

**언제:**
- 복잡한 학사 규정 해석
- 법률/의료 같은 정확도 중요 분야

**비용:** +$0.024 (1회만, 무시 가능)

---

### 시나리오 3: **완전 무료**
→ **KoSimCSE** (한국어만) 또는 **multilingual-e5-large**

**언제:**
- OpenAI API 비용 부담
- 인터넷 없는 환경

**단점:**
- 성능 5-10% 낮음
- 설정 복잡

---

## 직접 비교 테스트

### 테스트 방법

```python
# test_embeddings.py
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np

# 테스트 쿼리
query = "수강신청은 언제야?"
docs = [
    "2025학년도 1학기 수강신청은 2월 13일부터입니다.",
    "장학금 신청은 3월 1일부터 시작됩니다.",
    "도서관은 평일 오전 9시에 엽니다."
]

# OpenAI small
embeddings_small = OpenAIEmbeddings(model="text-embedding-3-small")
query_emb_small = embeddings_small.embed_query(query)
doc_embs_small = embeddings_small.embed_documents(docs)

# OpenAI large
embeddings_large = OpenAIEmbeddings(model="text-embedding-3-large")
query_emb_large = embeddings_large.embed_query(query)
doc_embs_large = embeddings_large.embed_documents(docs)

# 유사도 계산 (코사인)
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("text-embedding-3-small:")
for i, doc in enumerate(docs):
    sim = cosine_similarity(query_emb_small, doc_embs_small[i])
    print(f"  문서 {i+1}: {sim:.4f}")

print("\ntext-embedding-3-large:")
for i, doc in enumerate(docs):
    sim = cosine_similarity(query_emb_large, doc_embs_large[i])
    print(f"  문서 {i+1}: {sim:.4f}")
```

**예상 결과:**
```
text-embedding-3-small:
  문서 1: 0.8234 ✅ (수강신청 - 정답)
  문서 2: 0.3421
  문서 3: 0.2156

text-embedding-3-large:
  문서 1: 0.8456 ✅ (약간 더 높음)
  문서 2: 0.3198
  문서 3: 0.2034
```

**차이:** 대부분의 경우 **거의 비슷**

---

## 한국어 성능 특화 팁

### 1. **Normalize 추가**

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    # 차원 축소 (선택)
    dimensions=512  # 1536 → 512 (비용 1/3, 성능 -2%)
)
```

### 2. **Hybrid Search** (임베딩 + 키워드)

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# BM25 (키워드 매칭)
bm25 = BM25Retriever.from_documents(documents)

# Vector (의미 검색)
vector = vectorstore.as_retriever()

# 결합
ensemble = EnsembleRetriever(
    retrievers=[bm25, vector],
    weights=[0.3, 0.7]  # BM25 30%, Vector 70%
)
```

---

## 결론 및 추천

### 현재 설정 (text-embedding-3-small) 유지 ✅

**이유:**
1. **비용:** 거의 무료 ($0.004)
2. **성능:** 충분히 좋음 (62.3%)
3. **속도:** 빠름
4. **한국어:** 우수

### 업그레이드 고려 사항

**text-embedding-3-large로 변경:**
- 정확도가 중요한 프로덕션 환경
- 복잡한 법률/의료 문서
- 비용 무관 ($0.024는 무시 가능)

**무료 모델 고려:**
- OpenAI API 키 없을 때
- 완전 오프라인 환경
- 비용이 정말 중요할 때

---

## 빠른 변경 방법

### text-embedding-3-large로 변경

```python
# backend/rag_system.py:48-50
self.embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"  # small → large
)
```

**주의:**
- vectorstore 삭제 필요!
- 재생성 비용: +$0.024

### 무료 모델로 변경

```python
# backend/rag_system.py
from langchain_community.embeddings import HuggingFaceEmbeddings

self.embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large"
    # 또는 "BM-K/KoSimCSE-roberta" (한국어 특화)
)
```

---

## 실험 추천

1. **현재 모델 유지** (text-embedding-3-small)
2. 답변 품질 평가
3. 만족스럽지 않으면:
   - 먼저 **데이터 정제** (더 효과적!)
   - 그래도 안 되면 **large 시도**

**99%의 경우 small로 충분합니다!** ⭐

---

바꾸고 싶으신가요? 아니면 현재 설정 유지?
