"""
OpenAI Vision API를 사용한 이미지 텍스트 추출 (OCR)

기능:
1. Base64 인코딩된 이미지에서 텍스트 추출
2. 한국어 최적화
3. 표, 차트 등 복잡한 레이아웃 처리
"""

import json
import os
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv
import time

# 환경 변수 로드
load_dotenv()


class ImageTextExtractor:
    """이미지 텍스트 추출기"""

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        초기화

        Args:
            model: 사용할 모델 (gpt-4o 또는 gpt-4o-mini)
        """
        self.client = OpenAI()
        self.model = model

        # 모델별 비용 (1000 이미지당)
        self.costs = {
            "gpt-4o": 10.0,      # $10/1000 images
            "gpt-4o-mini": 3.0   # $3/1000 images
        }

        print(f"🤖 OpenAI Vision 초기화: {model}")
        print(f"💰 예상 비용: ${self.costs[model]}/1000 이미지\n")

    def extract_text(self, image_base64: str, alt_text: str = "") -> str:
        """
        단일 이미지에서 텍스트 추출

        Args:
            image_base64: Base64 인코딩된 이미지
            alt_text: 이미지 alt 속성 (힌트)

        Returns:
            추출된 텍스트
        """
        try:
            # 프롬프트 구성
            prompt = """이 이미지에서 모든 텍스트를 정확하게 추출해주세요.

**중요 규칙:**
1. 한국어와 영어 모두 정확히 추출
2. 날짜, 시간, 숫자는 매우 정확하게
3. 표나 리스트는 구조를 유지하며 마크다운 형식으로:
   - 표: | 컬럼1 | 컬럼2 |
   - 리스트: - 항목1
4. 여러 섹션이 있으면 구분해서 작성
5. 읽을 수 없는 부분만 [불명확]로 표시
6. 이미지 설명이나 추측은 절대 하지 말 것 (텍스트만!)

**출력 형식:**
제목이나 헤딩이 있으면:
# [제목]

본문:
[추출된 텍스트]
"""

            if alt_text:
                prompt += f"\n\n**힌트 (alt 텍스트):** {alt_text}"

            # API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "high"  # 고해상도 분석
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1  # 일관성 있는 추출
            )

            extracted_text = response.choices[0].message.content
            return extracted_text.strip()

        except Exception as e:
            print(f"      ❌ OCR 실패: {e}")
            return ""

    def process_images(self, data: List[Dict], save_interval: int = 10) -> List[Dict]:
        """
        여러 문서의 이미지 처리

        Args:
            data: 문서 데이터 리스트 (images 필드 포함)
            save_interval: 중간 저장 주기

        Returns:
            OCR 결과가 추가된 데이터 리스트
        """
        # 총 이미지 개수 계산
        total_images = sum(len(doc.get('images', [])) for doc in data)

        if total_images == 0:
            print("⚠️ 처리할 이미지가 없습니다.")
            return data

        print(f"📸 총 {total_images}개 이미지 OCR 시작...")
        print(f"💰 예상 비용: ${total_images * self.costs[self.model] / 1000:.2f}\n")

        processed_count = 0
        start_time = time.time()

        # 각 문서 처리
        for doc_idx, doc in enumerate(data, 1):
            images = doc.get('images', [])

            if not images:
                continue

            print(f"\n{'='*60}")
            print(f"문서 {doc_idx}/{len(data)}: {doc['url']}")
            print(f"이미지 {len(images)}개 처리 중...")
            print(f"{'='*60}")

            image_texts = []

            # 각 이미지 처리
            for img_idx, img in enumerate(images, 1):
                processed_count += 1

                print(f"  [{processed_count}/{total_images}] "
                      f"처리 중... ({img['size']/1024:.1f}KB)")

                # OCR 실행
                text = self.extract_text(img['data'], img.get('alt', ''))

                if text:
                    image_texts.append({
                        'url': img['url'],
                        'alt': img.get('alt', ''),
                        'text': text,
                        'size': img['size']
                    })
                    print(f"    ✅ 추출 완료 ({len(text)}자)")
                else:
                    print(f"    ⚠️ 텍스트 없음")

                # 진행률 표시
                progress = processed_count / total_images * 100
                elapsed = time.time() - start_time
                eta = (elapsed / processed_count) * (total_images - processed_count)

                print(f"    진행률: {progress:.1f}% | "
                      f"경과: {elapsed/60:.1f}분 | "
                      f"남은 시간: {eta/60:.1f}분")

                # API 레이트 리밋 방지 (1초 대기)
                time.sleep(1)

            # 이미지 텍스트를 문서에 추가
            if image_texts:
                # 이미지 콘텐츠를 별도 섹션으로
                doc['image_content'] = '\n\n' + '='*60 + '\n'
                doc['image_content'] += '📸 이미지에서 추출된 텍스트\n'
                doc['image_content'] += '='*60 + '\n\n'

                for i, img_text in enumerate(image_texts, 1):
                    doc['image_content'] += f"## 이미지 {i}\n"
                    if img_text['alt']:
                        doc['image_content'] += f"**Alt:** {img_text['alt']}\n\n"
                    doc['image_content'] += img_text['text'] + '\n\n'
                    doc['image_content'] += '-'*60 + '\n\n'

                # 원본 content와 병합
                doc['content'] = doc.get('text', '') + doc['image_content']

                print(f"\n  ✅ 문서 처리 완료: {len(image_texts)}개 이미지 텍스트 추가")

        # 최종 통계
        elapsed = time.time() - start_time
        actual_cost = processed_count * self.costs[self.model] / 1000

        print(f"\n{'='*60}")
        print(f"🎉 OCR 완료!")
        print(f"{'='*60}")
        print(f"처리된 이미지: {processed_count}개")
        print(f"소요 시간: {elapsed/60:.1f}분")
        print(f"실제 비용: ${actual_cost:.2f} (약 {actual_cost*1300:.0f}원)")
        print(f"{'='*60}\n")

        return data


def process_file(input_file: str, output_file: str, model: str = "gpt-4o-mini"):
    """
    JSON 파일 처리 (편의 함수)

    Args:
        input_file: 입력 JSON 파일 (images 필드 포함)
        output_file: 출력 JSON 파일
        model: 사용할 모델
    """
    print(f"📂 입력 파일: {input_file}")
    print(f"📂 출력 파일: {output_file}\n")

    # 데이터 로드
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📊 총 {len(data)}개 문서 로드\n")

    # OCR 처리
    extractor = ImageTextExtractor(model=model)
    data = extractor.process_images(data)

    # 저장
    print(f"💾 결과 저장 중: {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 저장 완료!\n")


# 테스트
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'ocr_result.json'
        model = sys.argv[3] if len(sys.argv) > 3 else 'gpt-4o-mini'

        process_file(input_file, output_file, model)
    else:
        print("사용법: python extract_image_text.py <입력파일> [출력파일] [모델]")
        print("예시: python extract_image_text.py crawled.json ocr_result.json gpt-4o-mini")
