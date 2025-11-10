# 이미지 텍스트 추출 가이드 (OCR)

## 문제 상황

학교 홈페이지에 이미지로 올라간 정보:
- 📅 수강신청 일정표 (엑셀 스크린샷)
- 📋 장학금 공지 (한글 파일 이미지)
- 📊 학사일정표
- 🎯 행사 포스터

현재 크롤러는 이미지 **건너뜀** → 중요 정보 누락!

---

## 해결 방법 비교

### 1. **OpenAI Vision API (GPT-4o)** ⭐⭐⭐⭐⭐ 추천!

**장점:**
- ✅ 한국어 인식 **최고 성능**
- ✅ 이미 OpenAI 사용 중 → 통합 쉬움
- ✅ 표, 차트, 복잡한 레이아웃도 이해
- ✅ 문맥까지 이해 (단순 OCR 이상)

**단점:**
- ❌ 유료 ($0.01/이미지)

**비용 예상:**
- 이미지 100개 = **$1** (1,300원)
- 이미지 500개 = **$5** (6,500원)

**적합한 경우:**
- 복잡한 문서 (표, 차트)
- 정확도 중요
- 이미지 수 적음 (< 500개)

---

### 2. **EasyOCR** ⭐⭐⭐⭐ 무료 추천!

**장점:**
- ✅ **완전 무료**
- ✅ 한국어 지원 우수
- ✅ 설치 쉬움
- ✅ 로컬 실행 (인터넷 불필요)

**단점:**
- ⚠️ GPU 권장 (CPU도 가능하지만 느림)
- ⚠️ 복잡한 레이아웃에 약함

**적합한 경우:**
- 예산 제한
- 단순 텍스트 이미지
- 이미지 많음

---

### 3. **Tesseract OCR**

**장점:**
- ✅ 무료
- ✅ 오픈소스 (가장 유명)

**단점:**
- ❌ 한국어 성능 낮음
- ❌ 설정 복잡
- ❌ 손글씨 인식 안 됨

**비추천** (한국어 프로젝트)

---

### 4. **CLOVA OCR (네이버)** ⭐⭐⭐⭐⭐

**장점:**
- ✅ 한국어 **최고 성능**
- ✅ 무료 티어 (월 1,000건)
- ✅ 한국 서비스 → 한국 문서 특화

**단점:**
- ⚠️ 네이버 클라우드 계정 필요
- ⚠️ 설정 복잡

**적합한 경우:**
- 한국어 문서 전문
- 월 1,000건 이하
- 무료로 고성능 원할 때

---

## 추천: OpenAI Vision API (간단 + 정확)

이미 OpenAI 사용 중이므로 **가장 쉽고 정확합니다!**

### 구현 방법

#### 1. 크롤러에 이미지 다운로드 추가

```python
# crawl_with_images.py
import requests
from bs4 import BeautifulSoup
import base64
import json
from pathlib import Path

def download_images(soup, base_url):
    """페이지의 모든 이미지 다운로드"""
    images = []

    for img in soup.find_all('img'):
        img_url = img.get('src')
        if not img_url:
            continue

        # 상대 URL을 절대 URL로 변환
        if img_url.startswith('/'):
            img_url = base_url + img_url
        elif not img_url.startswith('http'):
            continue

        # 이미지 다운로드
        try:
            response = requests.get(img_url, timeout=10)
            if response.status_code == 200:
                # Base64 인코딩 (OpenAI API 전송용)
                img_b64 = base64.b64encode(response.content).decode()
                images.append({
                    'url': img_url,
                    'data': img_b64,
                    'alt': img.get('alt', '')
                })
        except Exception as e:
            print(f"이미지 다운로드 실패: {img_url} - {e}")

    return images

def crawl_with_images(url):
    """이미지 포함 크롤링"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 텍스트 추출
    text = soup.get_text()

    # 이미지 다운로드
    images = download_images(soup, 'https://www.dyu.ac.kr')

    return {
        'url': url,
        'text': text,
        'images': images
    }
```

---

#### 2. OpenAI Vision으로 이미지 → 텍스트 변환

```python
# extract_image_text.py
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def extract_text_from_image(image_base64: str) -> str:
    """
    OpenAI Vision API로 이미지에서 텍스트 추출

    Args:
        image_base64: Base64 인코딩된 이미지

    Returns:
        추출된 텍스트
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # 또는 gpt-4o-mini (더 저렴)
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """이 이미지에서 모든 텍스트를 추출해주세요.

규칙:
1. 한국어와 영어 모두 정확히 추출
2. 표나 차트는 구조를 유지하며 마크다운으로
3. 날짜, 시간, 숫자는 정확히
4. 읽을 수 없는 부분은 [불명확]로 표시
5. 이미지 설명은 제외하고 텍스트만

출력 형식:
제목: [제목]
내용:
[내용]
"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"이미지 텍스트 추출 실패: {e}")
        return ""


def process_all_images(data_file: str, output_file: str):
    """모든 이미지에서 텍스트 추출"""

    # 데이터 로드
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_images = sum(len(item.get('images', [])) for item in data)
    print(f"📸 총 {total_images}개 이미지 처리 시작...")

    processed = 0

    # 각 문서의 이미지 처리
    for item in data:
        if 'images' not in item or not item['images']:
            continue

        image_texts = []

        for img in item['images']:
            processed += 1
            print(f"진행: {processed}/{total_images} - {img['url'][:50]}...")

            # OCR 실행
            text = extract_text_from_image(img['data'])

            if text:
                image_texts.append({
                    'url': img['url'],
                    'text': text
                })

        # 이미지에서 추출한 텍스트를 본문에 추가
        if image_texts:
            item['image_content'] = '\n\n---이미지 텍스트---\n\n'
            for img_text in image_texts:
                item['image_content'] += f"\n[이미지: {img_text['url']}]\n"
                item['image_content'] += img_text['text'] + '\n'

            # 원본 content와 병합
            item['content'] = item['text'] + item['image_content']

    # 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 완료! {output_file}에 저장됨")
    print(f"💰 예상 비용: ${total_images * 0.01:.2f}")


if __name__ == "__main__":
    process_all_images('crawled_with_images.json', 'data_with_ocr.json')
```

---

#### 3. 통합 크롤링 파이프라인

```python
# full_pipeline.py
"""
완전 자동화된 크롤링 → OCR → 정제 파이프라인
"""

import json
from crawl_with_images import crawl_with_images
from extract_image_text import process_all_images
from clean_data import clean_html, remove_duplicates, filter_low_quality

def full_pipeline(urls: list[str], output_file: str):
    """
    전체 파이프라인 실행

    1. 크롤링 (이미지 포함)
    2. OCR (이미지 → 텍스트)
    3. 데이터 정제
    """

    print("🚀 1단계: 웹 크롤링 시작...")
    raw_data = []
    for i, url in enumerate(urls, 1):
        print(f"  {i}/{len(urls)}: {url}")
        data = crawl_with_images(url)
        raw_data.append(data)

    # 임시 저장
    with open('temp_raw.json', 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 크롤링 완료: {len(raw_data)}개 페이지")

    # 이미지 개수 확인
    total_images = sum(len(item.get('images', [])) for item in raw_data)
    print(f"📸 발견된 이미지: {total_images}개")

    if total_images > 0:
        cost = total_images * 0.01
        print(f"💰 예상 OCR 비용: ${cost:.2f} (약 {cost*1300:.0f}원)")

        confirm = input("\nOCR 진행하시겠습니까? (y/n): ")
        if confirm.lower() != 'y':
            print("OCR 생략됨")
            return

        print("\n🔍 2단계: 이미지 OCR 시작...")
        process_all_images('temp_raw.json', 'temp_ocr.json')

        # OCR 결과 로드
        with open('temp_ocr.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("\n이미지 없음, OCR 생략")
        data = raw_data

    print("\n🧹 3단계: 데이터 정제 시작...")

    # 중복 제거
    data = remove_duplicates(data)
    print(f"  중복 제거: {len(data)}개 남음")

    # HTML 정제
    for item in data:
        item['content'] = clean_html(item['content'])
    print(f"  HTML 정제 완료")

    # 품질 필터링
    data = filter_low_quality(data)
    print(f"  품질 필터링: {len(data)}개 남음")

    # 최종 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 완료! {output_file}에 저장됨")
    print(f"최종 문서 수: {len(data)}개")


# 사용 예시
if __name__ == "__main__":
    urls = [
        'https://www.dyu.ac.kr/plaza/news/study-inform/',
        'https://www.dyu.ac.kr/academic/',
        # ... 더 추가
    ]

    full_pipeline(urls, 'final_data.json')
```

---

## EasyOCR 대안 (무료)

OpenAI 비용이 부담되면 무료 EasyOCR 사용:

### 설치

```bash
pip install easyocr
```

### 코드

```python
# easy_ocr.py
import easyocr
import base64
from io import BytesIO
from PIL import Image

# 리더 초기화 (한 번만)
reader = easyocr.Reader(['ko', 'en'], gpu=False)  # GPU 있으면 True

def extract_text_easyocr(image_base64: str) -> str:
    """EasyOCR로 텍스트 추출"""
    try:
        # Base64 → PIL Image
        img_data = base64.b64decode(image_base64)
        img = Image.open(BytesIO(img_data))

        # OCR 실행
        results = reader.readtext(img)

        # 텍스트 추출
        texts = [text for (bbox, text, prob) in results]

        return '\n'.join(texts)

    except Exception as e:
        print(f"EasyOCR 실패: {e}")
        return ""
```

**장단점:**
- ✅ 무료
- ✅ 단순 텍스트는 잘 인식
- ❌ 표/차트 레이아웃 무시
- ❌ 느림 (CPU 사용 시)

---

## 비용 vs 성능 비교

| 방법 | 비용 (100 이미지) | 한국어 성능 | 레이아웃 인식 | 속도 |
|------|------------------|------------|-------------|------|
| **GPT-4o** | $1 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **GPT-4o-mini** | $0.30 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **EasyOCR** | 무료 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **CLOVA OCR** | 무료 (1000/월) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Tesseract** | 무료 | ⭐⭐ | ⭐ | ⭐⭐⭐ |

---

## 실전 워크플로우

### Phase 1: 샘플 테스트
1. 이미지 10개만 수동 다운로드
2. GPT-4o-mini로 OCR 테스트
3. 결과 품질 확인
4. 비용 계산 (10개 × $0.003 = $0.03)

### Phase 2: 전체 실행
5. 이미지 개수 확인
6. 예상 비용 계산
   - 100개: $0.30 (gpt-4o-mini)
   - 500개: $1.50
7. 예산 괜찮으면 실행

### Phase 3: 결과 통합
8. OCR 텍스트 + 원본 텍스트 병합
9. 데이터 정제
10. RAG 시스템에 적용

---

## 추천 전략

### 시나리오 1: 예산 있음 ($5 이하)
→ **GPT-4o-mini** 사용
- 가장 정확
- 구현 쉬움
- 시간 절약

### 시나리오 2: 완전 무료 필요
→ **EasyOCR** 사용
- 무료
- 단순 텍스트는 OK
- 복잡한 레이아웃은 수동 검토

### 시나리오 3: 최고 품질 + 무료
→ **CLOVA OCR** (네이버)
- 월 1,000건 무료
- 한국어 최고
- 설정 복잡 (1회만)

---

## 즉시 시작 가이드

### 1. GPT-4o-mini로 테스트 (가장 쉬움)

```python
# test_single_image.py
from openai import OpenAI
import requests
import base64

client = OpenAI()

# 이미지 URL
img_url = "https://www.dyu.ac.kr/plaza/news/.../.jpg"

# 다운로드
response = requests.get(img_url)
img_b64 = base64.b64encode(response.content).decode()

# OCR
result = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "이 이미지의 모든 텍스트를 추출해주세요."},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{img_b64}"
            }}
        ]
    }]
)

print(result.choices[0].message.content)
```

실행:
```bash
python test_single_image.py
```

---

어떤 방법으로 시작하시겠어요?
1. **GPT-4o-mini** (추천 - 간단 + 정확)
2. **EasyOCR** (무료)
3. **샘플 먼저 테스트**

코드 작성해드릴까요?
