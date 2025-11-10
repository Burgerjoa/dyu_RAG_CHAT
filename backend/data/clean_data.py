"""
데이터 정제 스크립트

기능:
1. HTML 태그 제거
2. 중복 URL 제거
3. 불필요한 텍스트 정리
4. 너무 짧은 문서 필터링
"""

import json
import re
from typing import List, Dict
from collections import Counter
from bs4 import BeautifulSoup


def clean_html(content: str) -> str:
    """
    HTML 태그를 제거하고 텍스트를 정제

    Args:
        content: 원본 HTML 또는 텍스트

    Returns:
        정제된 텍스트
    """
    # BeautifulSoup으로 파싱
    soup = BeautifulSoup(content, 'lxml')

    # 불필요한 태그 완전 제거
    for tag in soup(['script', 'style', 'nav', 'footer', 'header',
                     'iframe', 'noscript', 'meta', 'link']):
        tag.decompose()

    # 텍스트 추출
    text = soup.get_text()

    # 중복 공백/줄바꿈 제거
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]  # 빈 줄 제거

    # 반복되는 패턴 제거 (네비게이션 메뉴 등)
    # 예: "Previous tab Next tab" 같은 패턴
    lines = [line for line in lines if not re.match(r'^(Previous|Next|tab|\||»|«)+\s*(Previous|Next|tab|\||»|«)*$', line)]

    # 특수 패턴 제거
    common_patterns = [
        r'^목록보기$',
        r'^인쇄$',
        r'^좋아요 \d+ 싫어요 \d+$',
        r'^Read more$',
        r'^조회 \d+$',
    ]

    filtered_lines = []
    for line in lines:
        skip = False
        for pattern in common_patterns:
            if re.match(pattern, line.strip()):
                skip = True
                break
        if not skip:
            filtered_lines.append(line)

    # 최종 텍스트 조합
    text = '\n'.join(filtered_lines)

    # 연속된 공백을 하나로
    text = re.sub(r'\s+', ' ', text)

    # 3개 이상 연속된 줄바꿈을 2개로
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def remove_duplicates(data: List[Dict]) -> List[Dict]:
    """
    URL 기준으로 중복 제거 (최신 것 유지)

    Args:
        data: 문서 리스트

    Returns:
        중복 제거된 문서 리스트
    """
    seen_urls = {}

    for item in data:
        url = item['url']
        # URL에서 쿼리 파라미터 제거하여 기본 URL만 비교
        base_url = url.split('?')[0]

        if base_url not in seen_urls:
            seen_urls[base_url] = item
        else:
            # 더 긴 컨텐츠를 가진 것을 선택
            if len(item['content']) > len(seen_urls[base_url]['content']):
                seen_urls[base_url] = item

    return list(seen_urls.values())


def filter_low_quality(data: List[Dict], min_length: int = 50) -> List[Dict]:
    """
    품질이 낮은 문서 필터링

    Args:
        data: 문서 리스트
        min_length: 최소 콘텐츠 길이

    Returns:
        필터링된 문서 리스트
    """
    filtered = []

    for item in data:
        content = item['content']

        # 너무 짧은 문서 제외
        if len(content) < min_length:
            continue

        # 의미 없는 문서 제외 (거의 숫자만 있거나)
        if len(re.findall(r'\d', content)) / len(content) > 0.5:
            continue

        # 반복되는 문자가 너무 많은 경우 제외
        if len(set(content)) / len(content) < 0.1:
            continue

        filtered.append(item)

    return filtered


def print_statistics(original_data: List[Dict], cleaned_data: List[Dict]):
    """
    데이터 정제 전후 통계 출력

    Args:
        original_data: 원본 데이터
        cleaned_data: 정제된 데이터
    """
    print("\n" + "="*60)
    print("📊 데이터 정제 통계")
    print("="*60)

    # 기본 통계
    print(f"\n원본 문서 수: {len(original_data):,}개")
    print(f"정제 후 문서 수: {len(cleaned_data):,}개")
    print(f"제거된 문서: {len(original_data) - len(cleaned_data):,}개 "
          f"({(1 - len(cleaned_data)/len(original_data))*100:.1f}% 감소)")

    # 컨텐츠 길이 통계
    original_lengths = [len(item['content']) for item in original_data]
    cleaned_lengths = [len(item['content']) for item in cleaned_data]

    print(f"\n평균 콘텐츠 길이:")
    print(f"  원본: {sum(original_lengths)/len(original_lengths):.0f}자")

    if cleaned_lengths:
        print(f"  정제 후: {sum(cleaned_lengths)/len(cleaned_lengths):.0f}자")
    else:
        print(f"  정제 후: 0자 (모든 데이터가 필터링됨)")

    total_original = sum(original_lengths)
    total_cleaned = sum(cleaned_lengths) if cleaned_lengths else 0

    print(f"\n총 텍스트 크기:")
    print(f"  원본: {total_original/1024/1024:.2f} MB")
    print(f"  정제 후: {total_cleaned/1024/1024:.2f} MB")

    if total_original > 0:
        print(f"  감소: {(1 - total_cleaned/total_original)*100:.1f}%")

    # URL 도메인 분포
    if cleaned_data:
        print(f"\n상위 URL 도메인:")
        domains = [item['url'].split('/')[2] if len(item['url'].split('/')) > 2 else item['url']
                   for item in cleaned_data]
        domain_counts = Counter(domains).most_common(5)
        for domain, count in domain_counts:
            print(f"  {domain}: {count}개")
    else:
        print(f"\n⚠️ 경고: 정제 후 남은 데이터가 없습니다!")

    print("="*60 + "\n")


def main():
    """메인 실행 함수"""
    input_file = '111.json'
    output_file = '111_cleaned.json'

    print(f"🚀 데이터 정제 시작: {input_file}")

    # 1. 데이터 로드
    print(f"\n1️⃣ 데이터 로드 중...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   ✅ {len(data):,}개 문서 로드 완료")
    except FileNotFoundError:
        print(f"   ❌ 파일을 찾을 수 없습니다: {input_file}")
        return
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON 파싱 오류: {e}")
        return

    original_data = data.copy()

    # 2. 중복 제거
    print(f"\n2️⃣ 중복 URL 제거 중...")
    before_count = len(data)
    data = remove_duplicates(data)
    after_count = len(data)
    print(f"   ✅ {before_count - after_count:,}개 중복 제거 ({after_count:,}개 남음)")

    # 3. HTML 정제
    print(f"\n3️⃣ HTML 태그 제거 및 텍스트 정제 중...")
    for i, item in enumerate(data):
        if i % 500 == 0:
            print(f"   진행: {i}/{len(data)} ({i/len(data)*100:.1f}%)")
        item['content'] = clean_html(item['content'])
    print(f"   ✅ 모든 문서 정제 완료")

    # 4. 저품질 문서 필터링
    print(f"\n4️⃣ 저품질 문서 필터링 중...")
    before_count = len(data)
    data = filter_low_quality(data, min_length=50)
    after_count = len(data)
    print(f"   ✅ {before_count - after_count:,}개 문서 제거 ({after_count:,}개 남음)")

    # 5. 통계 출력
    print_statistics(original_data, data)

    # 6. 저장
    print(f"5️⃣ 정제된 데이터 저장 중: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   ✅ 저장 완료!")

    # 7. 샘플 출력
    print(f"\n6️⃣ 정제 전후 비교 (첫 번째 문서):")
    print("\n" + "-"*60)
    print("📄 원본:")
    print("-"*60)
    print(original_data[0]['content'][:300] + "...")

    print("\n" + "-"*60)
    print("✨ 정제 후:")
    print("-"*60)
    # 정제된 데이터에서 같은 URL 찾기
    cleaned_sample = next((d for d in data if d['url'] == original_data[0]['url']), data[0])
    print(cleaned_sample['content'][:300] + "...")
    print("-"*60)

    print(f"\n🎉 데이터 정제 완료! {output_file} 파일을 확인하세요.")
    print(f"   다음 단계: backend/rag_system.py에서 data_path='data/111_cleaned.json'으로 변경")


if __name__ == "__main__":
    main()
