# 배포 가이드

## 전체 아키텍처

- **백엔드 (FastAPI)**: Render에 배포
- **프론트엔드 (Streamlit)**: Streamlit Community Cloud에 배포
- **데이터**: ChromaDB (벡터스토어는 런타임에 생성)

---

## 1단계: GitHub에 푸시

```bash
git add .
git commit -m "배포 준비: requirements 분리 및 환경변수 설정"
git push origin main
```

---

## 2단계: 백엔드 배포 (Render)

### 2-1. Render 계정 생성
1. https://render.com 접속
2. GitHub 계정으로 로그인
3. "New +" → "Web Service" 선택

### 2-2. 백엔드 설정
- **Repository**: `Burgerjoa/dyu_RAG_CHAT` 선택
- **Name**: `dyu-rag-backend` (원하는 이름)
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2-3. 환경 변수 설정
Render 대시보드에서 Environment Variables 추가:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### 2-4. 배포
- "Create Web Service" 클릭
- 배포 완료 후 URL 확인: `https://dyu-rag-backend.onrender.com`

**주의**:
- 첫 실행 시 벡터 DB 생성으로 5-10분 소요
- 무료 플랜은 15분 비활동 후 sleep 모드 (첫 요청 시 재시작)

---

## 3단계: 프론트엔드 배포 (Streamlit Cloud)

### 3-1. Streamlit Cloud 계정 생성
1. https://share.streamlit.io 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭

### 3-2. 프론트엔드 설정
- **Repository**: `Burgerjoa/dyu_RAG_CHAT`
- **Branch**: `main`
- **Main file path**: `frontend/app.py`

### 3-3. Advanced settings 클릭
**Python version**: `3.11`

**Secrets** (환경변수) 추가:
```toml
API_BASE_URL = "https://dyu-rag-backend.onrender.com"
```
**(2-4에서 확인한 Render URL 사용)**

### 3-4. 배포
- "Deploy!" 클릭
- 배포 완료 후 URL 확인: `https://your-app.streamlit.app`

---

## 4단계: 테스트

### 백엔드 테스트
```bash
curl https://dyu-rag-backend.onrender.com/health
```

응답:
```json
{
  "status": "healthy",
  "rag_system_initialized": true,
  "api_version": "1.0.0"
}
```

### 프론트엔드 테스트
1. Streamlit 앱 URL 접속
2. "수강신청은 언제야?" 질문 입력
3. 답변 및 출처 확인

---

## 트러블슈팅

### 백엔드가 시작되지 않음
- Render 로그 확인
- `OPENAI_API_KEY` 환경변수 확인
- `data/111.json` 파일 존재 확인

### 프론트엔드가 백엔드에 연결 안 됨
- Streamlit Secrets에 `API_BASE_URL` 확인
- Render 백엔드가 실행 중인지 확인
- CORS 설정 확인 (main.py)

### 벡터 DB 생성 실패
- OpenAI API 키 유효성 확인
- API 크레딧 잔액 확인
- 배치 처리 크기 줄이기 (rag_system.py의 batch_size)

---

## 비용 관리

### 무료 티어 제한
- **Render**: 750시간/월 (무료)
- **Streamlit Cloud**: 무제한 (무료)
- **OpenAI API**: 사용량 기반 (유료)

### OpenAI 비용 절감 팁
1. 벡터 DB는 한 번만 생성 (Render에서 자동 유지)
2. 캐싱 활용 (질문 중복 체크)
3. Top-K 값 줄이기 (현재 3 → 2)
4. 더 저렴한 모델 사용 (gpt-4o-mini → gpt-5-nano)

---

## 업데이트 방법

코드 수정 후:
```bash
git add .
git commit -m "업데이트 내용"
git push origin main
```

- Render: 자동 재배포
- Streamlit Cloud: 자동 재배포

벡터 DB 재생성이 필요한 경우:
1. Render 대시보드 → Manual Deploy → Clear build cache
2. 재배포

---

## 로컬 개발 환경

```bash
# 백엔드
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 프론트엔드 (별도 터미널)
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

로컬에서는 `.env` 파일에 `OPENAI_API_KEY` 설정 필요
