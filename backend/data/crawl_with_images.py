"""
이미지 포함 웹 크롤러

기능:
1. 웹페이지 텍스트 추출
2. 이미지 URL 수집 및 다운로드
3. Base64 인코딩 (OpenAI API 전송용)
"""

import requests
from bs4 import BeautifulSoup
import base64
from typing import Dict, List
from urllib.parse import urljoin, urlparse
import time


def is_valid_image(img_url: str) -> bool:
    """
    유효한 이미지 URL인지 확인

    Args:
        img_url: 이미지 URL

    Returns:
        유효 여부
    """
    # 이미지 확장자 체크
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

    # URL 파싱
    parsed = urlparse(img_url.lower())
    path = parsed.path

    # 확장자 체크
    if any(path.endswith(ext) for ext in valid_extensions):
        return True

    # 쿼리 파라미터에 확장자가 있을 수도 있음
    if any(ext in img_url.lower() for ext in valid_extensions):
        return True

    return False


def download_image(img_url: str, timeout: int = 10) -> Dict:
    """
    이미지 다운로드 및 Base64 인코딩

    Args:
        img_url: 이미지 URL
        timeout: 타임아웃 (초)

    Returns:
        이미지 정보 딕셔너리 (url, data, size)
    """
    try:
        response = requests.get(img_url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        if response.status_code != 200:
            return None

        # 이미지 크기 체크 (5MB 이하만)
        content_length = len(response.content)
        if content_length > 5 * 1024 * 1024:  # 5MB
            print(f"    ⚠️ 이미지 너무 큼 (건너뜀): {content_length/1024/1024:.1f}MB")
            return None

        # 너무 작은 이미지는 아이콘일 가능성 (10KB 이하 제외)
        if content_length < 10 * 1024:  # 10KB
            return None

        # Base64 인코딩
        img_b64 = base64.b64encode(response.content).decode('utf-8')

        return {
            'url': img_url,
            'data': img_b64,
            'size': content_length
        }

    except Exception as e:
        print(f"    ❌ 이미지 다운로드 실패: {img_url[:50]}... - {e}")
        return None


def extract_images(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """
    페이지에서 모든 이미지 추출

    Args:
        soup: BeautifulSoup 객체
        base_url: 기본 URL (상대경로 변환용)

    Returns:
        이미지 정보 리스트
    """
    images = []
    img_tags = soup.find_all('img')

    print(f"  📸 {len(img_tags)}개 이미지 태그 발견")

    for i, img in enumerate(img_tags, 1):
        # src 또는 data-src 속성에서 URL 추출
        img_url = img.get('src') or img.get('data-src')

        if not img_url:
            continue

        # 상대 URL을 절대 URL로 변환
        img_url = urljoin(base_url, img_url)

        # 유효성 체크
        if not is_valid_image(img_url):
            continue

        # alt 텍스트 추출
        alt_text = img.get('alt', '')

        print(f"    다운로드 중 ({i}/{len(img_tags)}): {img_url[:50]}...")

        # 이미지 다운로드
        img_data = download_image(img_url)

        if img_data:
            img_data['alt'] = alt_text
            images.append(img_data)
            print(f"    ✅ 성공 ({img_data['size']/1024:.1f}KB)")

        # 서버 부하 방지
        time.sleep(0.5)

    print(f"  ✅ 총 {len(images)}개 이미지 다운로드 완료")

    return images


def crawl_page_with_images(url: str) -> Dict:
    """
    단일 페이지 크롤링 (텍스트 + 이미지)

    Args:
        url: 크롤링할 URL

    Returns:
        페이지 데이터 딕셔너리
    """
    print(f"\n🔍 크롤링: {url}")

    try:
        # 페이지 요청
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()

        # HTML 파싱
        soup = BeautifulSoup(response.content, 'lxml')

        # 제목 추출
        title = soup.find('title')
        title = title.get_text().strip() if title else url

        # 텍스트 추출 (body만)
        body = soup.find('body')
        if body:
            text = body.get_text()
        else:
            text = soup.get_text()

        # 이미지 추출
        images = extract_images(soup, url)

        return {
            'url': url,
            'title': title,
            'text': text,
            'content': text,  # clean_data.py와 호환성
            'images': images,
            'image_count': len(images)
        }

    except Exception as e:
        print(f"  ❌ 크롤링 실패: {e}")
        return {
            'url': url,
            'title': url,
            'text': '',
            'content': '',
            'images': [],
            'image_count': 0,
            'error': str(e)
        }


def crawl_multiple_pages(urls: List[str]) -> List[Dict]:
    """
    여러 페이지 크롤링

    Args:
        urls: URL 리스트

    Returns:
        페이지 데이터 리스트
    """
    results = []
    total = len(urls)

    print(f"🚀 총 {total}개 페이지 크롤링 시작...\n")

    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"진행: {i}/{total} ({i/total*100:.1f}%)")
        print(f"{'='*60}")

        data = crawl_page_with_images(url)
        results.append(data)

        # 서버 부하 방지
        if i < total:
            time.sleep(2)

    # 통계
    total_images = sum(d['image_count'] for d in results)
    successful = sum(1 for d in results if 'error' not in d)

    print(f"\n{'='*60}")
    print(f"📊 크롤링 완료!")
    print(f"{'='*60}")
    print(f"성공: {successful}/{total}개 페이지")
    print(f"총 이미지: {total_images}개")
    print(f"{'='*60}\n")

    return results


# 테스트
if __name__ == "__main__":
    # 테스트 URL (학사공지 페이지)
    test_urls = [
        'https://www.dyu.ac.kr/plaza/news/study-inform/',
    ]

    results = crawl_multiple_pages(test_urls)

    # 결과 출력
    for result in results:
        print(f"\nURL: {result['url']}")
        print(f"제목: {result['title'][:50]}...")
        print(f"텍스트 길이: {len(result['text'])}자")
        print(f"이미지 개수: {result['image_count']}개")

        if result['images']:
            print("\n이미지:")
            for img in result['images'][:3]:  # 처음 3개만
                print(f"  - {img['url'][:70]}...")
                print(f"    Alt: {img['alt'][:50]}..." if img['alt'] else "    Alt: (없음)")
                print(f"    크기: {img['size']/1024:.1f}KB")
