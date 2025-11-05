import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse


class UniversityCrawler(CrawlSpider):
    name = 'university_crawler'

    # 도메인 설정 (allowed_domains에 맞게)
    allowed_domains = ['dyu.ac.kr']
    start_urls = ['https://www.dyu.ac.kr']

    # 커스텀 설정
    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',  # 이 줄 추가!
        'DEPTH_LIMIT': 3,  # 깊이 제한
        'DOWNLOAD_DELAY': 1,  # 요청 간격 (서버 부하 방지)
        'CONCURRENT_REQUESTS': 4,  # 동시 요청 수
        'LOG_LEVEL': 'INFO',  # 로그 레벨
    }

    # 크롤링 규칙
    rules = (
        Rule(
            LinkExtractor(
                allow_domains=['dyu.ac.kr'],  # 같은 도메인만
                deny=[
                    r'\.(jpg|jpeg|png|gif|pdf|zip|exe|css|js)$',  # 파일 제외
                    r'/download/',
                    r'/file/',
                ],
                unique=True,
                deny_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'zip', 'exe'],
            ),
            callback='parse_page',
            follow=True  # 계속 링크를 따라감
        ),
    )

    def parse_page(self, response):
        """각 페이지에서 데이터 추출"""

        # 디버깅: 어떤 페이지를 크롤링 중인지 출력
        self.logger.info(f'크롤링 중: {response.url}')

        # 제목 추출 (여러 방법 시도)
        title = (
                response.css('h1::text').get() or
                response.css('title::text').get() or
                '제목 없음'
        )

        # 본문 추출 (여러 선택자 시도)
        content_parts = []

        # 방법 1: 주요 태그들에서 텍스트 추출
        for selector in ['main', 'article', '[role="main"]', '#content', '.content']:
            texts = response.css(f'{selector} *::text').getall()
            if texts:
                content_parts = texts
                break

        # 방법 2: body 전체에서 추출 (위 방법이 실패한 경우)
        if not content_parts:
            content_parts = response.css('body *::text').getall()

        # 텍스트 정제
        content = ' '.join([t.strip() for t in content_parts if t.strip()])

        # 최소 길이 체크 (너무 짧은 페이지는 제외)
        if len(content) < 50:
            self.logger.warning(f'내용이 너무 짧음: {response.url}')
            return

        # 데이터 반환
        yield {
            'url': response.url,
            'title': title.strip(),
            'content': content[:5000],  # 너무 길면 잘라냄
            'content_length': len(content),
        }

    def parse_start_url(self, response):
        """시작 URL도 파싱"""
        return self.parse_page(response)