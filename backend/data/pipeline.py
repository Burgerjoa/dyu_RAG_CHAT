"""
전체 자동화 파이프라인

1. 웹 크롤링 (텍스트 + 이미지)
2. 이미지 OCR (OpenAI Vision)
3. 데이터 정제 (HTML 제거, 중복 제거)
4. 최종 JSON 생성
"""

import json
import os
from datetime import datetime
from crawl_with_images import crawl_multiple_pages
from extract_image_text import ImageTextExtractor
from clean_data import clean_html, remove_duplicates, filter_low_quality, print_statistics


class Pipeline:
    """데이터 파이프라인"""

    def __init__(self, output_dir: str = "output"):
        """
        초기화

        Args:
            output_dir: 출력 디렉토리
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 타임스탬프
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"🚀 파이프라인 초기화")
        print(f"📂 출력 디렉토리: {output_dir}\n")

    def run(self, urls: list, ocr_enabled: bool = True, ocr_model: str = "gpt-4o-mini"):
        """
        전체 파이프라인 실행

        Args:
            urls: 크롤링할 URL 리스트
            ocr_enabled: OCR 사용 여부
            ocr_model: OCR 모델 (gpt-4o 또는 gpt-4o-mini)

        Returns:
            최종 처리된 데이터
        """
        print("="*70)
        print(" "*20 + "📊 파이프라인 시작")
        print("="*70 + "\n")

        # ========== 1단계: 크롤링 ==========
        print("\n" + "="*70)
        print("1️⃣ 웹 크롤링 (텍스트 + 이미지)")
        print("="*70 + "\n")

        data = crawl_multiple_pages(urls)

        # 중간 저장
        crawled_file = os.path.join(self.output_dir, f'step1_crawled_{self.timestamp}.json')
        self._save_json(data, crawled_file)
        print(f"✅ 크롤링 결과 저장: {crawled_file}\n")

        # 통계
        total_images = sum(d.get('image_count', 0) for d in data)
        successful = sum(1 for d in data if 'error' not in d and len(d.get('text', '')) > 0)
        failed = len(data) - successful
        avg_text_length = sum(len(d.get('text', '')) for d in data) / len(data) if data else 0

        print(f"📊 크롤링 통계:")
        print(f"  - 총 페이지: {len(data)}개")
        print(f"  - 성공: {successful}개")
        print(f"  - 실패: {failed}개")
        print(f"  - 평균 텍스트 길이: {avg_text_length:.0f}자")
        print(f"  - 이미지: {total_images}개")

        if failed > 0:
            print(f"\n⚠️ {failed}개 페이지 크롤링 실패")
            for d in data:
                if 'error' in d or len(d.get('text', '')) == 0:
                    print(f"  - {d['url']}: {d.get('error', '텍스트 없음')}")

        # ========== 2단계: OCR (선택사항) ==========
        if ocr_enabled and total_images > 0:
            print("\n" + "="*70)
            print("2️⃣ 이미지 OCR (OpenAI Vision)")
            print("="*70 + "\n")

            # 비용 계산
            cost_per_1000 = {"gpt-4o": 10.0, "gpt-4o-mini": 3.0}
            estimated_cost = total_images * cost_per_1000[ocr_model] / 1000

            print(f"💰 예상 비용: ${estimated_cost:.2f} (약 {estimated_cost*1300:.0f}원)")
            print(f"📸 처리할 이미지: {total_images}개")
            print(f"🤖 사용 모델: {ocr_model}\n")

            # 확인
            confirm = input("OCR을 진행하시겠습니까? (y/n): ").strip().lower()

            if confirm == 'y':
                extractor = ImageTextExtractor(model=ocr_model)
                data = extractor.process_images(data)

                # 중간 저장
                ocr_file = os.path.join(self.output_dir, f'step2_ocr_{self.timestamp}.json')
                self._save_json(data, ocr_file)
                print(f"✅ OCR 결과 저장: {ocr_file}\n")
            else:
                print("⏭️ OCR 생략됨\n")
        else:
            if not ocr_enabled:
                print("\n⏭️ 2️⃣ OCR 비활성화 (생략)\n")
            else:
                print("\n⏭️ 2️⃣ 이미지 없음 (OCR 생략)\n")

        # ========== 3단계: 데이터 정제 ==========
        print("\n" + "="*70)
        print("3️⃣ 데이터 정제")
        print("="*70 + "\n")

        original_data = [d.copy() for d in data]

        # 3-1. 중복 제거
        print("  🔸 중복 URL 제거 중...")
        before = len(data)
        data = remove_duplicates(data)
        after = len(data)
        print(f"     제거: {before - after}개, 남음: {after}개\n")

        # 3-2. HTML 정제
        print("  🔸 HTML 태그 제거 및 텍스트 정제 중...")
        for i, item in enumerate(data):
            if i % 100 == 0 and i > 0:
                print(f"     진행: {i}/{len(data)} ({i/len(data)*100:.1f}%)")

            # content 필드 정제
            if 'content' in item:
                item['content'] = clean_html(item['content'])
            # text 필드도 정제 (있다면)
            if 'text' in item:
                item['text'] = clean_html(item['text'])

        print(f"     완료: {len(data)}개 문서 정제\n")

        # 3-3. 품질 필터링
        print("  🔸 저품질 문서 필터링 중 (최소 10자)...")
        before = len(data)
        data = filter_low_quality(data, min_length=10)
        after = len(data)
        print(f"     제거: {before - after}개, 남음: {after}개\n")

        # 데이터가 비어있는 경우 경고
        if after == 0:
            print("\n⚠️ 경고: 모든 데이터가 필터링되었습니다!")
            print("원인:")
            print("  1. 크롤링 실패 (페이지 접근 불가)")
            print("  2. 모든 문서가 10자 미만")
            print("  3. 중복 제거 시 모두 제거됨")
            print("\n해결 방법:")
            print("  - URL이 올바른지 확인")
            print("  - 학교 서버 접근 가능한지 확인")
            print("  - min_length 값을 더 작게 조정 (현재: 10)")
            print()

        # 통계 출력
        print_statistics(original_data, data)

        # 최종 저장
        final_file = os.path.join(self.output_dir, f'final_data_{self.timestamp}.json')
        self._save_json(data, final_file)

        print(f"\n✅ 최종 데이터 저장: {final_file}")

        # ========== 완료 ==========
        print("\n" + "="*70)
        print(" "*20 + "🎉 파이프라인 완료!")
        print("="*70)
        print(f"\n📁 출력 파일: {final_file}")
        print(f"📊 최종 문서 수: {len(data)}개")
        print(f"\n다음 단계:")
        print(f"  1. backend/main.py에서 data_path 변경:")
        print(f"     data_path=\"../{final_file}\"")
        print(f"  2. vectorstore 삭제 후 서버 재시작")
        print("="*70 + "\n")

        return data

    def _save_json(self, data: list, filename: str):
        """JSON 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    """메인 함수"""
    print("\n" + "="*70)
    print(" "*15 + "동양대학교 RAG 데이터 파이프라인")
    print("="*70 + "\n")

    # 크롤링할 URL 설정
    print("📝 크롤링할 페이지 설정\n")

    # 기본 URL (예시)
    default_urls = [
        # 학사공지
        'https://www.dyu.ac.kr/plaza/news/study-inform/',
        # 학사정보
        'https://www.dyu.ac.kr/academic/',
        # 장학/학자금
        'https://www.dyu.ac.kr/life/scholarship/',
        # 취업정보
        'https://www.dyu.ac.kr/employ/',
    ]

    print("기본 크롤링 대상:")
    for i, url in enumerate(default_urls, 1):
        print(f"  {i}. {url}")

    print("\n옵션:")
    print("  1) 기본 URL 사용")
    print("  2) URL 직접 입력")
    print("  3) 파일에서 URL 로드 (urls.txt)")

    choice = input("\n선택 (1-3): ").strip()

    if choice == '2':
        urls = []
        print("\nURL을 입력하세요 (빈 줄 입력 시 종료):")
        while True:
            url = input("URL: ").strip()
            if not url:
                break
            urls.append(url)
    elif choice == '3':
        try:
            with open('urls.txt', 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            print(f"\n✅ {len(urls)}개 URL 로드됨")
        except FileNotFoundError:
            print("\n❌ urls.txt 파일을 찾을 수 없습니다. 기본 URL 사용")
            urls = default_urls
    else:
        urls = default_urls

    if not urls:
        print("\n❌ URL이 없습니다. 종료합니다.")
        return

    # OCR 설정
    print("\n" + "="*70)
    print("🔍 OCR 설정")
    print("="*70 + "\n")

    print("이미지에서 텍스트를 추출하시겠습니까?")
    print("  y) 예 (OpenAI Vision 사용 - 유료)")
    print("  n) 아니오 (이미지 건너뛰기)")

    ocr_choice = input("\n선택 (y/n): ").strip().lower()
    ocr_enabled = (ocr_choice == 'y')

    ocr_model = "gpt-4o-mini"
    if ocr_enabled:
        print("\n사용할 모델:")
        print("  1) gpt-4o-mini (추천 - 저렴)")
        print("  2) gpt-4o (고성능 - 비쌈)")

        model_choice = input("\n선택 (1-2): ").strip()
        if model_choice == '2':
            ocr_model = "gpt-4o"

    # 파이프라인 실행
    pipeline = Pipeline(output_dir="output")
    pipeline.run(urls, ocr_enabled=ocr_enabled, ocr_model=ocr_model)


if __name__ == "__main__":
    main()
