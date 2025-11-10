# 🚀 자동화 파이프라인 사용 가이드

## 📋 개요

이미지 OCR을 포함한 전체 자동화 파이프라인:
1. **웹 크롤링** → 텍스트 + 이미지 수집
2. **이미지 OCR** → OpenAI Vision으로 텍스트 추출 (선택사항)
3. **데이터 정제** → HTML 제거, 중복 제거, 품질 필터링

## ⚙️ 사전 준비

### 1. 환경 변수 설정

`.env` 파일에 OpenAI API 키 필요:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

### 2. 필수 패키지 확인

이미 `requirements.txt`에 모두 포함되어 있습니다:
```bash
pip install -r requirements.txt
```

## 🎯 빠른 시작

### 방법 1: 자동화 파이프라인 (권장)

```bash
cd data
python pipeline.py
```

대화형 메뉴가 나타나면:
1. URL 선택 방식 선택 (기본 URL 사용 권장)
2. OCR 사용 여부 선택 (y/n)
3. OCR 모델 선택 (gpt-4o-mini 권장)

### 방법 2: 단계별 실행

#### Step 1: 크롤링만

```bash
python crawl_with_images.py
```

#### Step 2: OCR만 (이미 크롤링된 데이터에)

```bash
python extract_image_text.py step1_crawled_XXXXXXXX.json ocr_result.json gpt-4o-mini
```

#### Step 3: 데이터 정제만

```bash
python clean_data.py ocr_result.json final_cleaned.json
```

## 💰 비용 예상

### OCR 비용 (OpenAI Vision API)

| 모델 | 이미지당 비용 | 100개 이미지 | 1000개 이미지 |
|------|--------------|--------------|---------------|
| gpt-4o-mini | $0.003 | $0.30 (390원) | $3.00 (3,900원) |
| gpt-4o | $0.01 | $1.00 (1,300원) | $10.00 (13,000원) |

**권장**: gpt-4o-mini (성능 충분, 비용 1/3)

## 📂 출력 파일

파이프라인 실행 시 `data/output/` 디렉토리에 생성됩니다:

```
output/
├── step1_crawled_20250109_143022.json    # 크롤링 결과
├── step2_ocr_20250109_143522.json        # OCR 결과 (선택사항)
└── final_data_20250109_144022.json       # 최종 정제된 데이터 ⭐
```

## 🔄 RAG 시스템에 적용

### 1. 최종 데이터 확인

```bash
ls output/final_data_*.json
```

가장 최근 파일을 확인합니다.

### 2. 백엔드 설정 변경

`backend/main.py` 수정:
```python
rag_system = RAGSystem(data_path="../data/output/final_data_20250109_144022.json")
```

### 3. 벡터스토어 초기화

**중요**: 새로운 데이터를 사용하려면 기존 vectorstore 삭제 필수!

Windows PowerShell:
```powershell
Remove-Item -Recurse -Force backend/vectorstore/
```

Linux/Mac:
```bash
rm -rf backend/vectorstore/
```

### 4. 서버 재시작

```bash
cd backend
uvicorn main:app --reload
```

처음 시작 시 vectorstore가 자동으로 재생성됩니다 (5-10분 소요).

## 🎨 URL 커스터마이징

### urls.txt 파일 생성

`data/urls.txt` 파일을 만들고 크롤링할 URL을 한 줄씩 입력:

```text
https://www.dyu.ac.kr/plaza/news/study-inform/
https://www.dyu.ac.kr/academic/
https://www.dyu.ac.kr/life/scholarship/
https://www.dyu.ac.kr/employ/
https://www.dyu.ac.kr/plaza/news/normal-inform/
```

파이프라인 실행 시 옵션 3번 선택:
```
옵션:
  1) 기본 URL 사용
  2) URL 직접 입력
  3) 파일에서 URL 로드 (urls.txt)  ← 선택

선택 (1-3): 3
```

## ⚠️ 주의사항

### OCR 사용 시

1. **비용 확인**: 파이프라인이 예상 비용을 보여주면 확인 후 진행
2. **시간 소요**: 이미지 100개당 약 2-3분 소요
3. **API 레이트 리밋**: 자동으로 1초 대기 (변경 가능)

### 데이터 품질

정제 과정에서 제거되는 항목:
- 중복 URL
- 50자 미만의 짧은 문서
- HTML 태그 및 스크립트
- 과도한 공백 및 특수문자

## 🔍 문제 해결

### "OPENAI_API_KEY not found"
`.env` 파일 확인 및 API 키 설정

### "이미지 다운로드 실패"
- 네트워크 연결 확인
- 학교 서버 접근 권한 확인

### "JSONDecodeError"
- 크롤링 결과 파일 확인
- 파일 인코딩이 UTF-8인지 확인

### "Token limit exceeded"
- 배치 처리가 자동으로 적용됨
- 문제 지속 시 chunk_size 줄이기 (backend/rag_system.py)

## 📊 예상 워크플로우

**학기 초 또는 데이터 갱신 시**:

```bash
# 1. 전체 파이프라인 실행 (OCR 포함)
cd data
python pipeline.py
# → 기본 URL 사용
# → OCR 활성화 (y)
# → gpt-4o-mini 선택

# 2. 백엔드 설정 업데이트
# backend/main.py에서 data_path 변경

# 3. vectorstore 삭제
cd ..
Remove-Item -Recurse -Force backend/vectorstore/

# 4. 서버 재시작
cd backend
uvicorn main:app --reload
```

**정기 업데이트** (이미지 없는 경우):

```bash
# OCR 없이 빠른 크롤링
cd data
python pipeline.py
# → OCR 비활성화 (n)
```

## 📈 성능 팁

1. **OCR 선택적 사용**: 이미지가 중요한 페이지만 OCR 활성화
2. **URL 필터링**: 필요한 페이지만 크롤링
3. **배치 크롤링**: 여러 URL을 한 번에 처리
4. **중간 저장 활용**: 단계별 결과 파일 보관

## 🎓 다음 단계

1. ✅ 파이프라인으로 데이터 수집
2. ✅ RAG 시스템에 적용
3. 📊 답변 품질 모니터링
4. 🔄 정기적으로 데이터 업데이트
5. 🚀 프로덕션 배포 (DEPLOYMENT.md 참고)
